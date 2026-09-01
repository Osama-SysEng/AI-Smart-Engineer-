"""Controlled HTTP load probe for a staging deployment.

The probe is intentionally blocked for remote hosts unless the operator supplies
both an explicit confirmation and a bearer token. It must never be aimed at a
production endpoint without written capacity approval.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlparse

import httpx


@dataclass(frozen=True)
class Scenario:
    name: str
    path: str
    needs_auth: bool = False


SCENARIOS = (
    Scenario("liveness", "/api/v1/health/live"),
    Scenario("readiness", "/api/v1/health/ready"),
    Scenario("effective_permissions", "/api/v1/security/effective", needs_auth=True),
)


def percentile(values: list[float], fraction: float) -> float | None:
    """Return the nearest-rank percentile for non-empty latency samples."""
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(fraction * len(ordered)) - 1))
    return round(ordered[index], 2)


def assert_safe_target(base_url: str, allow_remote: bool) -> None:
    hostname = urlparse(base_url).hostname
    if not hostname:
        raise ValueError("Base URL must include an HTTP or HTTPS hostname")
    local_hosts = {"localhost", "127.0.0.1", "::1"}
    if hostname not in local_hosts and not allow_remote:
        raise ValueError("Remote targets require --allow-remote after capacity approval")


async def execute_scenario(
    client: httpx.AsyncClient,
    scenario: Scenario,
    token: str | None,
    repeats: int,
    semaphore: asyncio.Semaphore,
) -> list[dict]:
    async def one_request() -> dict:
        headers = {"Authorization": f"Bearer {token}"} if scenario.needs_auth and token else {}
        started = time.perf_counter()
        async with semaphore:
            try:
                response = await client.get(scenario.path, headers=headers)
                return {"scenario": scenario.name, "status": response.status_code, "latency_ms": round((time.perf_counter() - started) * 1000, 2)}
            except httpx.HTTPError as exc:
                return {"scenario": scenario.name, "status": 0, "latency_ms": round((time.perf_counter() - started) * 1000, 2), "error": type(exc).__name__}

    return await asyncio.gather(*(one_request() for _ in range(repeats)))


def summarize(results: list[dict]) -> dict:
    grouped: dict[str, list[dict]] = {}
    for item in results:
        grouped.setdefault(item["scenario"], []).append(item)
    output = {}
    for name, items in grouped.items():
        latencies = [item["latency_ms"] for item in items]
        succeeded = sum(200 <= item["status"] < 400 for item in items)
        output[name] = {
            "requests": len(items),
            "successful_requests": succeeded,
            "error_rate": round(1 - (succeeded / len(items)), 4),
            "latency_ms": {"p50": percentile(latencies, 0.50), "p95": percentile(latencies, 0.95), "p99": percentile(latencies, 0.99), "max": max(latencies, default=None)},
        }
    return output


async def run(args: argparse.Namespace) -> dict:
    assert_safe_target(args.base_url, args.allow_remote)
    token = os.getenv("LOADTEST_BEARER_TOKEN")
    active_scenarios = [scenario for scenario in SCENARIOS if not scenario.needs_auth or token]
    if not active_scenarios:
        raise ValueError("No active scenarios; provide LOADTEST_BEARER_TOKEN for authenticated coverage")
    async with httpx.AsyncClient(base_url=args.base_url.rstrip("/"), timeout=args.timeout_seconds) as client:
        batches = await asyncio.gather(
            *(execute_scenario(client, scenario, token, args.requests_per_scenario, asyncio.Semaphore(args.concurrency)) for scenario in active_scenarios)
        )
    results = [item for batch in batches for item in batch]
    return {"target": args.base_url, "configuration": {"concurrency": args.concurrency, "requests_per_scenario": args.requests_per_scenario}, "scenarios": [asdict(scenario) for scenario in active_scenarios], "summary": summarize(results)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run controlled AI-Smart-Engineer API load probes")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--requests-per-scenario", type=int, default=25)
    parser.add_argument("--timeout-seconds", type=float, default=10)
    parser.add_argument("--allow-remote", action="store_true")
    parser.add_argument("--output", default="reports/load/latest.json")
    args = parser.parse_args()
    if args.concurrency < 1 or args.requests_per_scenario < 1:
        parser.error("concurrency and requests-per-scenario must be positive")
    return args


if __name__ == "__main__":
    arguments = parse_args()
    report = asyncio.run(run(arguments))
    output = Path(arguments.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))

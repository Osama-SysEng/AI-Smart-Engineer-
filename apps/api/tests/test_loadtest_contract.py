"""Unit contracts for the non-destructive load-test harness."""
import pytest

from loadtests.authenticated_api_load import assert_safe_target, percentile, summarize


def test_remote_load_target_requires_explicit_opt_in():
    with pytest.raises(ValueError, match="allow-remote"):
        assert_safe_target("https://staging.example.com", allow_remote=False)
    assert_safe_target("http://localhost:8000", allow_remote=False)


def test_load_summary_reports_error_rate_and_percentiles():
    report = summarize([
        {"scenario": "ready", "status": 200, "latency_ms": 10.0},
        {"scenario": "ready", "status": 200, "latency_ms": 20.0},
        {"scenario": "ready", "status": 503, "latency_ms": 30.0},
    ])
    assert report["ready"]["error_rate"] == 0.3333
    assert report["ready"]["latency_ms"]["p95"] == 30.0
    assert percentile([], 0.95) is None

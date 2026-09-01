# Controlled Load Testing

The load harness verifies the API’s **staging** behavior under bounded concurrent traffic. It is not a declaration of production capacity, and it does not target a remote host unless the operator explicitly supplies `--allow-remote` after obtaining environment-owner approval.

| Scenario | Authentication | Purpose | Default request count |
|---|---:|---|---:|
| `/health/live` | No | Confirm process liveness path | 25 |
| `/health/ready` | No | Exercise database readiness path | 25 |
| `/security/effective` | Yes, if `LOADTEST_BEARER_TOKEN` exists | Exercise a session-bound authorization read | 25 |

Start a local or isolated staging stack, create a dedicated least-privilege load-test user, and set only its short-lived bearer token in the process environment. Then run `python apps/api/loadtests/authenticated_api_load.py --base-url http://localhost:8000 --concurrency 10 --requests-per-scenario 25`. The resulting JSON report is written to `reports/load/latest.json`; this location is ignored by release packaging and should not contain request bodies or credentials.

For a sanctioned staging run, increase load in stages rather than jumping directly to a target number: establish a baseline, raise concurrency gradually, observe database connections, CPU, queue depth, error rate, and p95/p99 latency, then stop on a breach of the agreed service objective. Retain the generated report with the release evidence and record the environment version, migration revision, and data-sanitization status.

> Do not execute load tests against production data, Internet-facing endpoints, ERP systems, or AI-provider quotas without written approval and a rollback plan.

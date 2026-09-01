# Security Baseline — 2026-08-23

This baseline records the evidence produced from the repository after adding server-side sessions, tenant-scoped RBAC, managed PostgreSQL controls, and the security-report workflow. It is an engineering snapshot, not a certification or penetration test.

| Control | Observed result | Evidence | Release interpretation |
|---|---|---|---|
| Dependency audit | Open dependency findings | `reports/security/pip-audit.json` | **Do not treat as a clean release gate.** Upgrade work remains required. |
| Python static analysis | Passed | `reports/security/bandit.json` | No Bandit finding in the scanned API source on this run. |
| OWASP SAST | Passed; 0 findings reported | `reports/security/semgrep.json` | Useful code-pattern coverage, not proof of absence of vulnerabilities. |
| Secret scan | Passed with local heuristic fallback | `reports/security/secret-heuristic.json` | Replace fallback with Gitleaks in the hardened CI image before production approval. |
| Auth/session tests | Passed | `apps/api/tests/test_security_sessions.py` | Covers refresh rotation, replay revocation, logout revocation, and tenant policy boundaries. |

## Open dependency remediation

The dependency audit identified findings in the current pinned stack, including `cryptography`, `python-jose`, `starlette`, `python-multipart`, `pillow`, `pdfminer-six`, `torch`, `transformers`, and the LangChain family. Some recommendations require major-version changes or have no fixed version listed. These should be handled through a compatibility-tested upgrade branch rather than by blindly changing pins in a production release.

The first remediation pass should prioritize Internet-facing parsing and authentication dependencies, then upgrade the AI and document-processing stack in isolated groups. Each group requires a fresh dependency audit, API regression run, document-sample validation on sanitized files, and a staged rollout plan. The raw report retains exact advisory identifiers and suggested fixed versions where the advisory database provides them.

## Security gates before a production cutover

The release owner should require a managed scanner image containing `pip-audit`, Bandit, Semgrep, and Gitleaks; all four must execute successfully, and the dependency gate must have either no actionable findings or documented, time-bound exceptions. A staging deployment must also demonstrate TLS-enforced PostgreSQL connectivity, successful migration to revision `0002`, session rotation and revocation, restrictive CORS, and a controlled load-test report.

> The report deliberately keeps unresolved dependency findings visible. Passing static analysis and a local secret heuristic does not compensate for vulnerable dependency versions.

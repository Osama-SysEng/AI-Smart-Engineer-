# Security Report

Generated: 2026-08-23T10:04:39Z

| Control | Status | Evidence |
|---|---|---|
| Dependency audit | findings_or_failure | pip-audit.json |
| Python static analysis | passed | bandit.json |
| OWASP SAST | passed | semgrep.json |
| Secret scan | passed_heuristic | secret-heuristic.json (fallback) |

A missing tool is not a clean result. CI must install all scanners and fail the release when a configured gate fails. The local secret heuristic is not equivalent to Gitleaks and is retained only as a transparent fallback.

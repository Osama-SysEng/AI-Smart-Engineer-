#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
report_dir="${SECURITY_REPORT_DIR:-$root_dir/reports/security}"
mkdir -p "$report_dir"

declare -A status
run_or_record() {
  local name="$1"
  shift
  if command -v "$1" >/dev/null 2>&1; then
    if "$@"; then status["$name"]="passed"; else status["$name"]="findings_or_failure"; fi
  else
    status["$name"]="tool_missing"
  fi
}

cd "$root_dir"
run_or_record "dependency_audit" pip-audit -r apps/api/requirements.txt -f json -o "$report_dir/pip-audit.json"
run_or_record "static_analysis" bandit -r apps/api/src -f json -o "$report_dir/bandit.json"
run_or_record "owasp_sast" semgrep --config p/owasp-top-ten --json --output "$report_dir/semgrep.json" apps/api/src
if command -v gitleaks >/dev/null 2>&1; then
  run_or_record "secret_scan" gitleaks detect --source . --report-format json --report-path "$report_dir/gitleaks.json" --no-banner
  secret_evidence="gitleaks.json"
else
  if node tools/secret-scan.mjs --root . --output "$report_dir/secret-heuristic.json"; then status["secret_scan"]="passed_heuristic"; else status["secret_scan"]="findings_or_failure"; fi
  secret_evidence="secret-heuristic.json (fallback)"
fi

{
  echo "# Security Report"
  echo
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "| Control | Status | Evidence |"
  echo "|---|---|---|"
  echo "| Dependency audit | ${status[dependency_audit]} | pip-audit.json |"
  echo "| Python static analysis | ${status[static_analysis]} | bandit.json |"
  echo "| OWASP SAST | ${status[owasp_sast]} | semgrep.json |"
  echo "| Secret scan | ${status[secret_scan]} | ${secret_evidence} |"
  echo
  echo "A missing tool is not a clean result. CI must install all scanners and fail the release when a configured gate fails. The local secret heuristic is not equivalent to Gitleaks and is retained only as a transparent fallback."
} > "$report_dir/summary.md"

cat "$report_dir/summary.md"

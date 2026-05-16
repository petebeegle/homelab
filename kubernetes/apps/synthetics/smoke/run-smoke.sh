#!/usr/bin/env bash
set -uo pipefail

summary_pattern='^SMOKE_RUN_SUMMARY '
start_seconds="$(date +%s)"

set +u
tmpdir=$TMPDIR
playwright_command=$SMOKE_PLAYWRIGHT_COMMAND
set -u

if [ -z "$tmpdir" ]; then
  tmpdir=/tmp
fi

if [ -z "$playwright_command" ]; then
  playwright_command='npm run test'
fi

log_file="$(mktemp "$tmpdir/synthetic-smoke.XXXXXX.log")"

cleanup() {
  rm -f "$log_file"
}
trap cleanup EXIT

logfmt_quote() {
  node -e 'const value = String(process.argv[1] || "").replace(/[\r\n\t]+/g, " "); process.stdout.write(JSON.stringify(value));' "$1"
}

emit_fallback_summary() {
  local command_status="$1"
  local status="success"
  local failed_count="0"
  local failed_tests=""
  local end_seconds
  local duration_seconds

  end_seconds="$(date +%s)"
  duration_seconds=$((end_seconds - start_seconds))
  if (( duration_seconds < 0 )); then
    duration_seconds=0
  fi

  if (( command_status != 0 )); then
    status="failed"
    failed_tests="playwright execution failed before reporter summary"
  fi

  printf 'SMOKE_RUN_SUMMARY status=%s failed_count=%s failed_tests=%s duration_seconds=%s\n' \
    "$status" \
    "$failed_count" \
    "$(logfmt_quote "$failed_tests")" \
    "$duration_seconds"
}

set +e
bash -c "$playwright_command" 2>&1 | tee "$log_file"
playwright_status=$?
set -e

if ! grep -q "$summary_pattern" "$log_file"; then
  emit_fallback_summary "$playwright_status"
fi

exit "$playwright_status"

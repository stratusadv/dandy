#!/usr/bin/env bash
set -euo pipefail

case "${AI_API_KEY:-}" in
    ''|test-key|changeme|your-api-key|placeholder)
        echo "repl-smoke needs a real AI_API_KEY in development.env (dotenv-load)" >&2
        exit 1
        ;;
esac

repo="$PWD"
scratch="$(mktemp -d)"
cd "$scratch"
fail() {
    echo "" >&2
    echo "REPL SMOKE FAILED: $1" >&2
    echo "Scratch project kept for inspection: $scratch" >&2
    exit 1
}

cat > "$scratch/repl_smoke_driver.py" <<'PY'
import sys
from unittest import mock


def run_repl(scripted_lines):
    import dandy.interfaces.cli.main as cli_main

    with mock.patch(
        'dandy.interfaces.cli.tui.tui.Tui.get_user_input', side_effect=list(scripted_lines)
    ):
        sys.argv = ['dandy']
        cli_main.main()


if __name__ == '__main__':
    run_repl(sys.argv[1:])
PY

run_dandy() {
    timeout 600 env PYTHONPATH="$repo" "$repo/.venv/bin/python" \
        "$scratch/repl_smoke_driver.py" "$@"
}

echo "=== run 1: fresh project, one turn (auto-saves a session) ==="
run_dandy \
    'Remember the code word BANANA. Just reply with ok.' \
    '/quit' > "$scratch/run1.out" 2>&1 || fail "run 1 crashed (see $scratch/run1.out)"

grep -qF 'none yet' "$scratch/run1.out" \
    || fail "run 1 banner did not show the empty session state"

session_file="$(ls "$scratch"/.dandy/agent/sessions/*.json 2>/dev/null | head -n 1 || true)"
[ -n "$session_file" ] || fail "run 1 did not auto-save a session"
session_name="$(basename "$session_file" .json)"
echo "run 1: auto-saved session \"$session_name\""

echo "=== run 2: resume the session, ask for the code word ==="
run_dandy \
    "/resume $session_name" \
    'What was my code word? Reply with just that single word.' \
    '/quit' > "$scratch/run2.out" 2>&1 || fail "run 2 crashed (see $scratch/run2.out)"

grep -qF "1 saved, latest: $session_name" "$scratch/run2.out" \
    || fail "run 2 banner did not show the saved session"
grep -qi 'banana' "$scratch/run2.out" \
    || fail "run 2 did not answer from the resumed session context"

rm -rf "$scratch"
echo "REPL SMOKE OK: session \"$session_name\" auto-saved on turn 1, resumed on run 2, code word recalled"

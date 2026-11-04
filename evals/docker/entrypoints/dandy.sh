#!/usr/bin/env bash
source /entrypoints/common.sh

export PYTHONPATH=/dandy-lib:/eval
export DANDY_SETTINGS_MODULE=dandy_settings

python3 /eval/usage_proxy.py > /workdir/proxy.log 2>&1 &
proxy_pid=$!
sleep 1

status=0
timeout -k 30 "${AGENT_TIMEOUT_SECONDS:-1800}" python3 /dandy-lib/dandy/interfaces/cli/main.py "$AGENT_PROMPT" \
  > /workdir/transcript.log 2>&1 || status=$?
kill "$proxy_pid" 2>/dev/null || true
wait "$proxy_pid" 2>/dev/null || true

capture_final_diff
echo "AGENT_EXIT=$status" > /workdir/agent.exit
exit 0

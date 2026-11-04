#!/usr/bin/env bash
source /entrypoints/common.sh

cd /workdir
status=0
timeout -k 30 "${AGENT_TIMEOUT_SECONDS:-1800}" opencode run "$AGENT_PROMPT" -m stratus/stratus.turbo --auto --format json \
  > /workdir/transcript.json 2> /workdir/stderr.log || status=$?

capture_final_diff
echo "AGENT_EXIT=$status" > /workdir/agent.exit
exit 0

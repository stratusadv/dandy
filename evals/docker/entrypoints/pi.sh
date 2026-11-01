#!/usr/bin/env bash
source /entrypoints/common.sh

cd /workdir
status=0
timeout 1200 pi -p "$AGENT_PROMPT" \
  --model stratus/stratus.turbo \
  --extension /eval/pi-stratus.ts \
  --session-dir /workdir/.pi-sessions \
  --mode json > /workdir/transcript.json 2> /workdir/stderr.log || status=$?

capture_final_diff
echo "AGENT_EXIT=$status" > /workdir/agent.exit
exit 0

#!/usr/bin/env bash
source /entrypoints/common.sh

cd /workdir
status=0
timeout 1200 crush --data-dir /workdir/.crush-data run "$AGENT_PROMPT" -m stratus/stratus.turbo \
  > /workdir/transcript.log 2>&1 || status=$?

capture_final_diff
echo "AGENT_EXIT=$status" > /workdir/agent.exit
exit 0

#!/usr/bin/env bash
# Shared preamble: materialize the task workdir and baseline git state.
set -euo pipefail

cp -r /task/. /workdir/
cd /workdir
git init -q
git config user.email eval@local
git config user.name eval-baseline
git add -A
git commit -qm 'baseline'

capture_final_diff() {
  git add -A
  git diff --cached > /workdir/final.diff
  git diff --cached --stat > /workdir/final.diff.stat || true
}

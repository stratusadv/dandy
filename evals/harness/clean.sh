#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

if [ -n "${1:-}" ]; then
  rm -rf "evals/runs/$1"
  echo "removed evals/runs/$1"
else
  echo "usage: clean.sh <stamp>" >&2
  exit 2
fi

ids=$(docker ps -aq --filter label=dandy-eval=1 || true)
if [ -n "$ids" ]; then
  # shellcheck disable=SC2086
  docker rm -f $ids
  echo "removed leftover dandy-eval containers"
fi

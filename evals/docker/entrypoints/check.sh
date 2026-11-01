#!/usr/bin/env bash
set -uo pipefail
cd /workdir
rm -rf tests
cp -r /hidden-tests tests
python3 -m unittest discover -s tests -t . -p 'test_*.py' -v 2>&1 | tee /workdir/check.log
status=${PIPESTATUS[0]}
{
  echo '---'
  echo "CHECK_STATUS=$status"
} >> /workdir/check.log
exit "$status"

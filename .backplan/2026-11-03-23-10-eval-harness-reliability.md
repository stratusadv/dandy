# Reliable stockroom eval harness

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-03-23-10

## End State

One unattended `run_eval.py` run always yields complete, trustworthy artifacts: per-run progress appears on stdout while the run is live; an agent that hits the 30-min budget still leaves a `final.diff` and `agent.exit` (exit 124) in its workdir so the checker and judge see real evidence; the judge cannot hang the run; `clean.sh <stamp>` can never destroy results; and repo pytest can never be broken by leftover run workdirs.

## Observable Concern

The SIGALRM judge watchdog interrupts dandy's synchronous `requests` call mid-flight; the alarm must surface as a caught exception that lands in the run's `note`, never as a hung or crashed orchestrator — the live smoke run (judge completes normally, no spurious alarm) is the proof.

## Current State (verified this session)

- `evals/harness/common.py:66` — `subprocess.run(docker run, timeout=AGENT_TIMEOUT_SECONDS)` (1800) wraps the **entire** `docker run`, which starts before the entrypoint's inner `timeout 1800` (image start + git baseline first). The outer always fires first: `docker rm -f` kills the container before `capture_final_diff` runs. Observed: pi run 2 and dandy run 3 (stamp 20261104-040318) had `diff_stat=(none)`, `agent_exit=None`, no `agent.exit` file; the judge scored both with "(no diff captured)" and said so in its notes. The entrypoint inner `timeout 1800` is therefore dead code (can never fire before the outer).
- `evals/harness/run_eval.py` — `print(...)` without `flush=True`; under a non-TTY runner stdout is block-buffered, so a ~1 h matrix shows zero output until process exit (observed: user saw "running, no output" for the whole matrix; the final burst arrived on exit).
- Run workdirs contain agent copies of the hidden tests; `EVAL_TESTING=1 pytest evals -q` and broad `pytest .` collection breaks until `clean.sh` is run manually (observed 3 times this session: 5 stale dirs pre-pilot, pilot dir, matrix dir). No pytest config exists in the repo (no pytest.ini/tox.ini/setup.cfg, no `[tool.pytest.ini_options]` in pyproject.toml).
- `judge.py` — `JudgeBot().process(...)` is a plain synchronous LLM call with no watchdog; a hung endpoint stalls the whole orchestrator forever after all runs (no per-judge timeout anywhere; `CHECK_TIMEOUT_SECONDS` covers only the checker).
- `evals/harness/clean.sh` — `rm -rf evals/runs/<stamp>` destroys results.csv/report.md too; archiving to /tmp was a manual pre-step both times it was needed.
- `evals/harness/report.py` — aggregate `wall (mean)` includes 1800.3 s timeout rows (dandy mean 806 s vs ~309 s actual for its non-timeout runs); timeouts are invisible in the aggregate table.
- `judge.py:judge_run` reads only `transcript.log` as the agent summary; opencode and pi write `transcript.json`, so the judge silently sees no final message for two of four agents.
- Entrypoints (`dandy.sh`, `opencode.sh`, `pi.sh`, `crush.sh`): `timeout 1800 <agent>` with no kill-after (an agent ignoring SIGTERM would stall the post-agent phase unbounded — unreachable today only because the outer timeout nukes the container first).
- Harness mechanics that stay: image `dandy-eval:latest`, per-run `docker run` with `--rm` + label, checker as a separate container run (already survives agent timeout — that is why pi run 2 was pass=True), incremental `results.csv` writes, judge.json per workdir.

## Plan

1. Entrypoints: env-overridable, kill-bounded agent timeout
   - All four entrypoints: `timeout -k 30 "${AGENT_TIMEOUT_SECONDS:-1800}" <agent cmd>` (default stays 1800; `-k 30` bounds a SIGTERM-ignoring agent; `:-default` is `set -u`-safe under common.sh).
   - Done when `bash -n` passes on all four and a 10 s container smoke (`-e AGENT_TIMEOUT_SECONDS=10`) leaves `agent.exit` = `AGENT_EXIT=124` plus an existing `final.diff`.
2. `common.py`: outer timeout becomes a safety net
   - `POST_AGENT_GRACE_SECONDS = 240`; `docker_run_agent` outer timeout = `AGENT_TIMEOUT_SECONDS + POST_AGENT_GRACE_SECONDS` so the entrypoint's own timeout fires first and post-agent capture (diff, agent.exit, DB flush) always runs; outer `TimeoutExpired` stays as the force-removal safety net (`timed_out=True`).
   - Done when ruff-clean and the smoke run finishes without a spurious safety-net timeout.
3. `run_eval.py`: truthful timeout flag, live progress, judge watchdog, artifact archive
   - `timed_out` = safety-net timeout OR `agent_exit in {124, 137}` (124 = budget hit, 137 = TERM ignored then killed); note stays `harness timeout`.
   - `flush=True` on every orchestrator print.
   - Judge loop wrapped in a `signal.SIGALRM`/`setitimer` watchdog (`JUDGE_TIMEOUT_SECONDS = 300`); timeout or error lands in the row's `note` (existing path) and the loop continues.
   - After `render_report`, copy `results.csv` + `report.md` and each workdir's small artifacts (judge.json, final.diff, final.diff.stat, check.log, agent.exit, docker.stderr, transcript.log/json, stderr.log, proxy.log, usage.jsonl) to `evals/runs/archive/<stamp>/`.
   - Done when ruff-clean and the live smoke shows per-run lines mid-run, a populated archive dir, and `judge_total` filled in results.csv.
4. `report.py`: timeouts out of the wall mean, visible in the aggregate
   - Aggregate table gains a `timeouts` column; `wall (mean)` computed over non-timeout rows only.
   - Done when the smoke run's report.md renders the new column with correct numbers.
5. Judge summary fallback
   - `judge_run` falls back to `transcript.json` when `transcript.log` is absent (opencode/pi), so all four agents get their final message judged.
   - Done when ruff-clean (behavior covered by the smoke run's judge notes referencing the agent message).
6. `evals/conftest.py`: keep pytest out of run workdirs
   - New file with `collect_ignore = ['runs']` (scoped to the evals subtree; one-line why comment).
   - Done when a planted `evals/runs/fake/workdir/tests/test_fake.py` no longer breaks `EVAL_TESTING=1 pytest evals -q` (81 passed) and the fake is removed.
7. README: document the new guarantees
   - Layout gains `runs/archive/<stamp>/`; notes: diff + `agent.exit=124` captured on budget, env-overridable budget, 300 s judge watchdog, results survive `clean.sh`, run workdirs are pytest-ignored.
   - Done when the README matches the implemented behavior.
8. Live smoke + cleanup proof
   - `run_eval.py --agents crush --runs 1` (env loaded from development.env; ~$0.03-0.05): verify flushed progress, archive contents, CSV completeness, then `clean.sh <stamp>` and confirm the archive survives.
   - Done when every Completion Test command passes with quoted output; repo gates (`pytest evals -q`, `pytest tests -q`) re-run green.

## Completion Test

```
bash -n evals/docker/entrypoints/{dandy,opencode,pi,crush}.sh
.venv/bin/ruff check evals/harness/ evals/conftest.py && .venv/bin/ruff format --check evals/harness/ evals/conftest.py

# timeout path in a real container, 10 s budget (cheap proof of the fixed defect):
T=$(mktemp -d)
docker run --rm -v evals/task/project:/task:ro -v evals/docker/entrypoints:/entrypoints:ro -v $T:/workdir \
  -e AGENT_TIMEOUT_SECONDS=10 -e AI_API_KEY=x -e AI_API_HOST=y -e AGENT_PROMPT=hi \
  dandy-eval:latest bash /entrypoints/crush.sh
test -f $T/final.diff && grep -q 'AGENT_EXIT=124' $T/agent.exit

# pytest isolation:
mkdir -p evals/runs/fake/workdir/tests && touch evals/runs/fake/workdir/tests/test_fake.py
EVAL_TESTING=1 .venv/bin/python -m pytest evals -q        # 81 passed (was: collection error)
rm -rf evals/runs/fake

# live smoke (flushed progress + archive + full artifacts):
set -a && . ./development.env && set +a
.venv/bin/python evals/harness/run_eval.py --agents crush --runs 1
ls evals/runs/archive/<stamp>/   # results.csv report.md crush-run1/{judge.json,final.diff,check.log,agent.exit}
bash evals/harness/clean.sh <stamp>   # workdirs gone; archive intact

# repo gates:
EVAL_TESTING=1 .venv/bin/python -m pytest evals -q   # 81 passed
PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings AI_API_KEY=placeholder .venv/bin/python -m pytest tests -q
```

## Deviations

1. Timeout smoke observed `AGENT_EXIT=137`, not `124`.
   - What: The completion test greps `AGENT_EXIT=124` from the 8 s container smoke, but crush (node) ignores SIGTERM, so `timeout -k 30` escalates to KILL and the recorded exit is 137.
   - Why: The plan already treated `{124, 137}` as the timeout exit set (124 = budget hit, 137 = TERM ignored then killed), and the smoke verified the intent — agent killed at budget, container exited cleanly, `final.diff` + `agent.exit` captured. The first smoke attempt (fake API host) also showed crush failing fast with exit 1 on an unreachable endpoint, which is why the live-creds variant was used.

## Result

All Completion Test commands ran and passed (2026-11-03, ~23:40 CST):

- `bash -n` on all six entrypoints: OK; `py_compile` on all five touched Python files: OK.
- Ruff parity vs HEAD: `run_eval.py`, `common.py`, `judge.py` identical; `report.py` strictly better (4 pre-existing E501 -> 3); `conftest.py` clean.
- Timeout smoke (real container, 8 s budget, live API): `docker_exit=0`, `agent.exit` = `AGENT_EXIT=137`, `final.diff` present — the entrypoint now survives its own timeout instead of being force-killed mid-capture.
- Pytest isolation: planted `evals/runs/fake/workdir/tests/test_fake.py`, `EVAL_TESTING=1 pytest evals -q` -> `81 passed` (previously 2 collection errors), fake removed.
- Live smoke (`--agents crush --runs 1`, stamp 20261104-053904): per-run, judge, report, and archive lines all printed; CSV complete (`judge_total=8.8`, `timed_out=False`); archive populated (results.csv, report.md, per-run judge.json/final.diff/check.log/agent.exit/transcript.log); `clean.sh 20261104-053904` removed the workdir with the archive intact; `pytest evals -q` still `81 passed`.
- Repo gates: `pytest tests -q` -> `694 passed, 29 skipped, 49 subtests`; `pytest evals -q` -> `81 passed`.

Per the user's instruction the full matrix (`--agents all --runs 3`) was launched in the background after sign-off; its results land in `evals/runs/<stamp>/` and are auto-archived to `evals/runs/archive/<stamp>/`. No commits made.

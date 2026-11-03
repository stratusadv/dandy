# EVAL_TESTING gate + repo-runnable eval tests

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-03-08-55

## End State

The eval hidden tests are gated on the `EVAL_TESTING` env var (renamed from
`EVAL`), and with `EVAL_TESTING=1` they actually run **in the repo** — against
the reference solution (task project overlaid with `solution/`) — passing
15/15; without the var, `pytest .` skips them; the Docker checker flow keeps
working via `check.sh` exporting `EVAL_TESTING=1`.

## Observable Concern

Repo mode must target a correct overlay (project + every `solution/` file
mapped onto `stockroom/<relpath>`, built generically, not hardcoded to the
two current filenames), and container mode must stay exactly as it is today
(flat `/workdir` with `seed.json` beside the hidden tests' parent) — a layout
detection that misfires in either direction breaks the eval harness or makes
the in-repo check vacuous.

## Current State

- Gate (added yesterday): `evals/task/hidden_tests/test_stockroom.py:20-24` —
  `eval_test = unittest.skipUnless(bool(os.environ.get('EVAL')), ...)`
  decorating both `StockroomCliTest` and `StockroomOpsImportTest`;
  `evals/docker/entrypoints/check.sh:6` does `export EVAL=1`; `evals/README.md`
  mentions `EVAL` in two layout lines.
- Container layout (works): the check container mounts the per-run host dir at
  `/workdir` (the agent's final state, flat: `seed.json`, `stockroom/`,
  `TASK.md` at top level — `common.sh` does `cp -r /task/. /workdir/`), copies
  `/hidden-tests` to `/workdir/tests`, then `unittest discover -s tests -t .`.
  The test module computes `PROJECT = parents[1]` = `/workdir`,
  `SEED = PROJECT/'seed.json'` — correct there.
- Repo layout (broken): `evals/task/hidden_tests/`, `evals/task/project/`
  (`seed.json` + `stockroom/` package + `TASK.md` + `.gitignore`),
  `evals/task/solution/` containing **only** `cli.py` and `ops.py` — the fixed
  versions of `project/stockroom/cli.py` and `project/stockroom/ops.py`
  (verified by diff: solution adds the `summary` command, `json` import, etc.).
  The test module points `PROJECT = evals/task`, so locally `seed.json` and the
  `stockroom` package are both missing → 15 errors.
- The buggy `project/` state is intentional (it is what agents start from), so
  running the hidden tests against it in-repo is meaningless; the only correct
  in-repo target is the reference solution.
- `evals/` and `evals/task/` have no `__init__.py` (only `hidden_tests/` does),
  so pytest imports the module as `hidden_tests.test_stockroom` with
  `evals/task` on `sys.path`; `StockroomOpsImportTest` imports `stockroom.*` in
  the test process, which only works if the stockroom package root is
  importable.
- `AGENTS.md` and the `justfile` have no evals/EVAL references at all;
  `hidden_tests/__pycache__/` is covered by the root `.gitignore`.

## Plan

1. Rename the env var to `EVAL_TESTING`
   - `test_stockroom.py`: gate on `os.environ.get('EVAL_TESTING')` with
     falsy-value semantics — unset, `''`, and `'0'` are OFF (note: `bool()`
     alone would treat the string `'0'` as truthy), any other non-empty value
     is ON — + updated gate comment; `check.sh`: `export EVAL_TESTING=1`;
     `evals/README.md`: both mentions.
   - Done when `grep -rn "EVAL" evals/` shows only `EVAL_TESTING` references.
     `env -u EVAL_TESTING pytest evals` and `EVAL_TESTING=0 pytest evals` both
     report `15 skipped`.
2. Repo-mode layout in `test_stockroom.py`
   - `TASK = Path(__file__).resolve().parents[1]`. If `(TASK/'seed.json').is_file()`
     → container mode: `PROJECT = TASK`, `SEED = TASK/'seed.json'` (exactly
     today's behavior).
   - Else repo mode: `PROJECT = tempfile.mkdtemp(prefix='dandy-eval-solution-')`;
     `shutil.copytree(TASK/'project', PROJECT, dirs_exist_ok=True)`; copy every
     file under `TASK/'solution'` onto `PROJECT/'stockroom'/<relpath>`;
     `SEED = TASK/'project'/'seed.json'`; `sys.path.insert(0, str(PROJECT))`;
     `atexit.register(shutil.rmtree, PROJECT, ignore_errors=True)`.
   - Done when `EVAL_TESTING=1 pytest evals -q` → `15 passed` in the repo.
3. Docs
   - `evals/README.md`: the hidden_tests layout line notes the
     `EVAL_TESTING` gate and that in-repo they run against a solution overlay;
     add a one-line "running locally" note (`EVAL_TESTING=1 python -m pytest
     evals -q`).
   - `AGENTS.md` Testing approach: one line — evals hidden tests skip unless
     `EVAL_TESTING` is set; in-repo they verify the reference solution.
   - Done when `just docs-tests` still passes.
4. Gate
   - `EVAL_TESTING=1 ... pytest evals -q` → `15 passed`.
   - `EVAL_TESTING=1 ... python -m unittest discover
     -s evals/task/hidden_tests -t . -p 'test_*.py'` → `Ran 15 tests ... OK`
     (harness runner parity).
   - No var: `pytest . -q` → green with `15 skipped`, 0 failed.
   - Ruff on touched files vs HEAD (mirror-path method): no new findings.
   - `just lint-imports` (6 kept) and `just docs-tests`.
   - Done when all green.

## Completion Test

1. `cd /home/nathanj/PycharmProjects/dandy && EVAL_TESTING=1
   DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m
   pytest evals -q` → `15 passed`.
2. `EVAL_TESTING=1 ... .venv/bin/python -m unittest discover
   -s evals/task/hidden_tests -t . -p 'test_*.py'` → `OK` (15 run, 0 failed).
3. Gate OFF, both negative states, both runners:
   - `env -u EVAL_TESTING ... pytest evals -q` → `15 skipped`, 0 failed.
   - `EVAL_TESTING=0 ... pytest evals -q` → `15 skipped`, 0 failed.
   - `EVAL_TESTING=0 ... python -m unittest discover
     -s evals/task/hidden_tests -t . -p 'test_*.py'` → `OK (skipped=15)`.
4. `... .venv/bin/python -m pytest . -q` (no EVAL_TESTING) → 0 failed,
   15 skipped.
5. `grep -rn "EVAL" evals/ AGENTS.md` → only `EVAL_TESTING` occurrences.
6. Ruff mirror-path diff: identical findings for
   `evals/task/hidden_tests/test_stockroom.py` vs HEAD.
7. `just lint-imports` → 6 kept; `just docs-tests` → strict build success.

## Deviations

1. Gate must treat `EVAL_TESTING=0` (and empty) as OFF; completion test covers
   both negative states
    - What: per user redirect, the gate predicate is falsy-value-aware
      (unset / `''` / `'0'` → skip) instead of plain `bool(os.environ.get(...))`,
      and the completion test explicitly verifies the unset and `=0` states
      under both pytest and unittest discover.
    - Why: the string `'0'` is truthy in Python, so the original one-line gate
      would run the eval tests under `EVAL_TESTING=0`.

## Observed Output (completion test)

1. `EVAL_TESTING=1 ... pytest evals -q` → `15 passed in 0.69s`.
2. `EVAL_TESTING=1 ... python -m unittest discover
   -s evals/task/hidden_tests -t . -p 'test_*.py'` → `OK` (15 run, 0 failed).
3. Gate OFF, both negative states:
   - `env -u EVAL_TESTING ... pytest evals -q` → `15 skipped in 0.08s`.
   - `EVAL_TESTING=0 ... pytest evals -q` → `15 skipped in 0.07s`.
   - `EVAL_TESTING=0 ... python -m unittest discover ...` → `OK (skipped=15)`.
4. `... pytest . -q` (no EVAL_TESTING) → `672 passed, 15 skipped, 49 subtests
   passed in 258.86s` (a first full run showed 1 failed in
   `tests/application/bot/test_bot_instances.py` — a `@live_llm_test` that hit
   a live-endpoint flake; it passed in isolation and in the re-run).
5. `grep -rn "EVAL" evals/ AGENTS.md` → only `EVAL_TESTING` occurrences (plus
   two stale gitignored `.pyc` cache files).
6. Ruff mirror-path diff for `evals/task/hidden_tests/test_stockroom.py` →
   `IDENTICAL_RULESET` vs HEAD.
7. `just lint-imports` → `Contracts: 6 kept, 0 broken.`; `just docs-tests` →
   strict build success.

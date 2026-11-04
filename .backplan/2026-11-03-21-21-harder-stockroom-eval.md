# Harder stockroom eval task

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-03-21-21

## End State

`evals/task/` holds a v2 stockroom task — a ~1.5k-line multi-module project with a (sku, location)-keyed data model loaded from the old one-row-per-SKU seed, 6+ planted bugs (several only surfacing across command sequences), 4 missing commands with exact output contracts, Decimal half-up money math, a ~150-row seed with rounding/boundary traps, and a ~50-case EVAL_TESTING-gated hidden suite — such that: the reference solution passes the whole hidden suite (observed green), the pristine tree fails a measured majority of it (observed), `AGENT_TIMEOUT_SECONDS` and all four entrypoint `timeout` values are 1800, and a live `run_eval.py --agents all --runs 3` matrix completes with a visible pass-rate / judge-score spread across the four CLIs in `results.csv` / `report.md` (push-to-limit target: even the best agent drops runs; no perfect 12/12 sweep expected).

## Observable Concern

Difficulty calibration is blind: the most likely failure mode is a subtle spec/test/solution mismatch — a hidden-test value the spec doesn't actually force, or a reference solution that passes the tests but violates the spec — which turns "hard" into "impossible" and makes every agent fail for the same wrong reason, destroying the discrimination the task exists for. Mitigation: every expected test value is derived from the reference solution's actual behavior (never hand math), the pristine-tree failure map is recorded and checked against the intended bug list, and a dandy-only x3 pilot gates the full matrix.

## Current State

- **Saturated task**: `evals/task/project/` is ~190 lines (cli.py 86, ops.py 73, data.py 31) with 4 isolated one-line bugs (add overwrites instead of merges; remove rejects full-quantity via `>=`; `total_value` truncates with `int()`; `low_stock` uses `<` instead of `<=`) plus one missing command (`summary`); 15 flat hidden tests; 6-row seed.
- **No discrimination**: today's runs — 014334, 020905 — have all four agents passing nearly everything at judge 9.5-10.0 (dandy 9/10 across four sets including one exit-1 flake; pi/crush 100%).
- **Harness is task-agnostic** and needs almost no changes: `run_eval.py` (agents x runs, docker `--rm` per run, usage capture, judge via dandy `JudgeBot` on stratus.thinking, `results.csv` + `report.md`); `check.sh` copies hidden tests into the container, exports `EVAL_TESTING=1`, runs `python3 -m unittest discover`; the in-repo overlay mechanism in `hidden_tests/test_stockroom.py` copies `project/` to a temp dir and overlays `solution/*` into `stockroom/` (solution files must live at stockroom-package-relative paths).
- **Timeouts are two-layered**: `AGENT_TIMEOUT_SECONDS = 1260` in `evals/harness/common.py` (docker-level) and `timeout 1200` hardcoded in all four entrypoints (`dandy.sh`, `opencode.sh`, `pi.sh`, `crush.sh`).
- **Prompt** (`common.py:build_prompt`) is "read TASK.md, make it behave exactly as specified" + TASK.md inlined — any spec change lands through TASK.md alone.
- **Docker image** `dandy-eval:latest` bakes the other three CLIs; the dandy package and the task are bind-mounted read-only at run time, so no rebuild is needed for this change.
- **Costs** (stratus.turbo $1/$5 per Mtok): dandy's no-planning runs cost $0.07-0.14 each; a 4x3 matrix with a ~2-3x harder task is roughly $3-8 of API spend, wall time bounded by 3 sequential runs per agent (agents parallel).
- `evals/harness/*.py` is part of the pre-existing ruff/format version-drift set (15 files at HEAD) — new eval code must match HEAD ruff findings, not "clean".

## Design (the v2 task)

**Model.** Rows are keyed by `(sku, location)`; a SKU's stock may be split across locations. `seed.json` keeps the old shape (at most one row per sku) — loading it must work, and the first mutation writes new-style state (one row per (sku, location), sorted, zero-count rows dropped on save). `name` and `unit_price` are per-SKU attributes: adding with a differing name or price for an existing SKU is a domain error (exit 1).

**Commands** (spec lives in TASK.md; exact contracts):
- `add SKU NAME LOCATION COUNT UNIT_PRICE` — add to the (sku, location) row, creating it if needed; attribute-conflict rule above; positive-int COUNT or exit 2.
- `remove SKU COUNT [LOCATION]` — omit LOCATION: remove from the lexicographically first location holding that SKU's stock (subtle, spec-stated); exact-quantity removal allowed; unknown SKU or insufficient at that location exit 1; non-positive COUNT exit 2.
- `move SKU FROM TO` — move all units of (sku, FROM) into (sku, TO), merging into an existing TO row (no duplicate rows); unknown SKU or empty FROM exit 1.
- `transfer SKU FROM TO COUNT` — **missing**; move exactly COUNT units, creating the TO row; insufficient at FROM exit 1.
- `list` — `sku\tlocation\tname\tcount\tunit_price(.2f)` sorted by (sku, location).
- `value [LOCATION]` — Decimal half-up sum of count*unit_price (optionally location-filtered), printed 2 decimals.
- `low [THRESHOLD]` (default 5) — SKUs whose **total** count across locations is at or below threshold: `sku\ttotal`, sorted by sku.
- `summary` — **missing**; one JSON object `{"low_stock_count", "total_skus", "total_units", "total_value"}` on per-SKU totals.
- `report` — **missing**; one JSON object keyed by location: `{"A1": {"skus": n, "units": n, "value": x.xx}, ...}`, locations sorted, only locations with rows.
- `validate` — **missing**; invariants (duplicate (sku, location) rows, negative count, non-positive unit_price, empty sku/name/location, name/price inconsistency within a SKU): one `INVALID: <reason>` line per violation on stderr (deterministic order), exit 1; clean file prints nothing, exit 0.
- Money: exact decimal arithmetic, ROUND_HALF_UP to 2 places (the seed plants X.XX5 values where float `round()` disagrees).

**Codebase** (~1.5k lines, all stdlib):
- `stockroom/data.py` — correct: `Item` (sku, location, name, count, unit_price), old/new load, save (sorted, zero rows dropped).
- `stockroom/ops.py` — business logic; planted bugs: add overwrites instead of merging; remove rejects exact full quantity; low_stock compares per-row instead of per-SKU total (only wrong once a SKU is split — sequence-dependent); move creates a duplicate row instead of merging (surfaces via `validate` and double-counted `value` after the sequence move-then-value).
- `stockroom/pricing.py` — money helpers; planted bug: `round_money` uses `float` + built-in `round()` instead of Decimal ROUND_HALF_UP (wrong only on planted seed values).
- `stockroom/cli.py` — argparse CLI; planted bug: non-positive COUNT on `remove` exits 1 instead of 2 (exit-code matrix trap); plus the four missing commands.
- `stockroom/legacy_report.py` — correct but ugly legacy CSV renderer (string-built, old style); spec forbids rewriting it; a hidden test imports it and checks its output (anti-"refactor the world" check).
- `tools/nightly_restock.py` — maintenance script that restocks low SKUs via `ops` (a consumer proving function signatures/behavior); a hidden test runs it.
- `seed.json` — ~150 old-format rows generated programmatically: counts at 4/5/6 boundaries, several count*price pairs landing exactly on X.XX5 (float-round vs half-up traps), a few SKUs with 0/1 counts, location codes A1-D4.

**Hidden suite** (~50 cases, `EVAL_TESTING`-gated, same overlay mechanism): per-SKU unit ops (merge, exact remove, split totals, move merge), pricing rounding cases (exact X.XX5 values), loader back-compat + save normalization, CLI contracts for every command, the default-location remove rule, sequences (add -> transfer -> remove -> value -> summary; move -> value double-count; mutation preserves split rows on re-load), full exit-code matrix, `report`/`summary`/`validate` exact-output contracts, scale (whole-seed totals), nightly_restock run, legacy_report import+output. Every expected value is computed by running the reference solution, never by hand.

**Solution** — corrected `ops.py`, `cli.py`, `pricing.py` under `solution/` (stockroom-package-relative paths, matching the overlay).

**Harness** — `AGENT_TIMEOUT_SECONDS = 1800` in `common.py`; `timeout 1800` in all four entrypoints; `evals/README.md` task description + baseline notes updated. Nothing else changes (prompt, judge, docker, check flow are all task-agnostic).

## Plan

1. Write the v2 `TASK.md` spec
   - Exact contracts for every command, the (sku, location) model, attribute-conflict rule, default-location rule, money/rounding rule, exit-code matrix, legacy/no-rewrite rules. This is the single source of truth for tests and solution.
   - Done when the spec reads as unambiguous: each command has inputs, outputs (exact format), error cases with exit codes, and an example-free but fully determinate contract.
2. Build the project tree
   - `data.py` (correct), `ops.py`/`pricing.py`/`cli.py` with the planted bugs, `legacy_report.py`, `tools/nightly_restock.py`, and a generator script that emits the ~150-row `seed.json` with the boundary/rounding traps (generator run once, seed committed, generator kept in the task dir or dropped after use).
   - Done when the pristine project imports, `python3 -m stockroom --file seed.json list` runs (old-style, with the planted bugs visible), and `legacy_report` + `nightly_restock` run.
3. Write the hidden test suite
   - ~50 EVAL_TESTING-gated cases per the design above, keeping the existing file layout, gate, and in-repo overlay mechanism.
   - Done when the suite executes against the pristine tree and the failure set is recorded; failures map to the planted bugs + missing commands (no test failing for an unexpected reason).
4. Write the reference solution and make both verifications green
   - Corrected `ops.py`, `cli.py`, `pricing.py` under `solution/`; expected test values taken from running this solution (CLI output + JSON), not hand math.
   - Done when `EVAL_TESTING=1 .venv/bin/python -m pytest evals -q` is fully green AND the pristine-tree run shows a measured majority of failures whose causes match the intended bug list.
5. Harness + docs updates
   - `AGENT_TIMEOUT_SECONDS = 1800`; `timeout 1800` in `dandy.sh`/`opencode.sh`/`pi.sh`/`crush.sh`; `evals/README.md` (task description, timeout note, current-baseline section replaced by v2 results after step 6).
   - Done when no `1200`/`1260` remains in `evals/` and the README matches the new task; repo gates still green (`pytest tests -q`, ruff parity vs HEAD, `just lint-imports`, `just docs-tests`).
6. Pilot, then the full matrix
   - `run_eval.py --agents dandy --runs 3` first: confirm the task is in the difficulty band (some dandy failures expected; no systematic "impossible" failures), and fix any spec/test mismatch found.
   - Then `run_eval.py --agents all --runs 3` (background, ~1-1.5 h): read `results.csv`/`report.md`.
   - Done when the matrix report exists and shows a spread: pass rates differ across agents (target < 60% overall; if all agents still sweep 12/12, the task is not hard enough — record a deviation and iterate on step 2-4 difficulty before closing).

## Completion Test

```
EVAL_TESTING=1 .venv/bin/python -m pytest evals -q
    # reference overlay: full hidden suite green (quote the pass count)
EVAL_TESTING=1 .venv/bin/python -m unittest discover -s evals/task/hidden_tests -t . -p 'test_*.py'
    # pristine tree (in-repo form): measured failures recorded, majority red
.venv/bin/python -m pytest tests -q            # repo suite still green
just lint-imports                              # contracts still keep
.venv/bin/python evals/harness/run_eval.py --agents dandy --runs 3
    # pilot: difficulty in band, no systematic impossible-failures
.venv/bin/python evals/harness/run_eval.py --agents all --runs 3
    # full matrix: report.md + results.csv with a cross-agent spread in
    # pass/wall/tokens/judge (quote the aggregate table)
```

## Deviations

1. `remove` with a non-positive COUNT exits 0 on the pristine tree, not 1.
    - What: The planted cli bug is `type=int` on the `remove` subparser; with the planted `>=` ops bug, `remove SKU 0` is a silent no-op (exit 0) and `remove SKU -N` corrupts the file (count increases) instead of exiting 1 as the v1 bug list assumed.
    - Why: Recorded while deriving the pristine failure map; the spec (exit 2 for non-positive COUNT) and the hidden test are unchanged — only the description of the pristine behavior is corrected.
2. Cleaned the five stale `evals/runs/<stamp>/` directories with `evals/harness/clean.sh`.
   - What: Removed gitignored run artifacts (20261104-014334, -015902, -020244, -020905, -031045) after copying 031045's `results.csv`/`report.md` to `/tmp/eval-baseline-031045-*`.
   - Why: Their `workdir/tests/test_stockroom.py` copies (v1) broke collection of the documented completion command `EVAL_TESTING=1 .venv/bin/python -m pytest evals -q`; the new matrix runs will create fresh stamps anyway.
3. Pilot (dandy x3, stamp 20261104-033912) swept 3/3 — matrix runs before any deepening.
   - What: The plan's step 6 expected "some dandy failures" from the pilot; instead dandy passed all 3 runs (judge 9.3/9.5/9.9, wall 347.2/399.8/111.9s, all green on the full 81-test suite). The full `--agents all --runs 3` matrix was launched on that evidence rather than deepening difficulty first.
   - Why: The user-locked goal is cross-CLI discrimination, and the deepening trigger in the plan is "all agents still sweep 12/12" — a matrix-wide condition that only the full run can answer. v1 data showed all four CLIs sweep an easy task, so the unknown is the other three CLIs on v2. If the matrix sweeps 12/12, a further deviation will be recorded and the task deepened (new interaction, per the pilot caveat: isolated one-liners are what models currently one-shot) before closing.
4. Post-pilot hardening: closed the `report()` key-order gap and fixed the stale task description in the harness report.
   - What: The pilot judge observed dandy's `report()` builds location keys in first-appearance order, which the hidden suite could not catch (dict-equality comparisons ignore key order; the seed file's first-appearance order happens to equal location order). Added a `top_level_key_order` helper (`object_pairs_hook` pair-order parse, separator-agnostic) and asserted `['A1', 'B1']` on the unsorted F1 fixture (`test_report_fixture`, first file row is in B1) and replaced the vacuous sorted check in `test_report_seed`. Also replaced the hardcoded v1 task description at `evals/harness/report.py:36` with the v2 one.
   - Why: The spec says report keys are "in location order"; a first-appearance-order implementation passed the suite as written. Both gates re-verified after the change: solution overlay 81/81 green, pristine flat-copy still 42/81 red (36 failures + 6 errors, same causes). Pilot artifacts archived to `/tmp/eval-pilot-033912-*` and the pilot run dir cleaned (same procedure as deviation 2).

## Result

Full matrix (stamp `20261104-040318`, `--agents all --runs 3`, wall ~58 min): **8/12 pass, no 12/12 sweep — the deepening branch did not trigger; the End State is met.**

```
| agent    | passed | wall (mean) | cost (total) | judge (mean) |
|---|---|---|---|---|
| dandy    | 2/3    | 806s        | $8.5450      | 8.9          |
| opencode | 2/3    | 717s        | $2.5602      | 8.5          |
| pi       | 2/3    | 757s        | $7.2254      | 8.9          |
| crush    | 2/3    | 590s        | $0.0981      | 8.6          |
```

Failure modes (this is where the CLIs discriminate):

- `crush` run 1 (1 failure): `report` keys in first-appearance order — `test_report_fixture` `['B1','A1']` vs `['A1','B1']`.
- `pi` run 3 (1 failure): the same `test_report_fixture` first-appearance-order bug.
- `dandy` run 3: harness timeout at 1800s after 6,722,903 in-tokens; at check time 80/81 with the same `test_report_fixture` failure; no diff captured.
- `opencode` run 1 (9 failures): money values serialized as strings via `money_str`, breaking the JSON-number contract for summary/report/nightly, plus a stray empty `.t` file (lowest judge score, 6.8).

The post-pilot `test_report_fixture` key-order assertion (deviation 4) caught 3 of the 4 failed runs — the exact gap the pilot judge had found in dandy's first-appearance-order `report()`. Secondary signals: opencode run 3 (pass, judge 8.8) silently regressed `low 0` to exit 2 via `positive_int`; opencode run 2 scored 9.8; crush is the cheapest agent by far (~30k in-tokens/run, $0.098 total); pi run 2 and dandy run 3 each burned 6.4M/6.7M in-tokens hitting the locked 30-min budget (wall-time tail of the matrix; no timeout change made, per the locked ~30-min requirement).

Completion test output (all run after the matrix):

```
EVAL_TESTING=1 .venv/bin/python -m pytest evals -q
    # 81 passed in 2.56s (reference overlay)
EVAL_TESTING=1 PYTHONPATH=$T python -m unittest discover -s tests -t . -p 'test_*.py'   # pristine flat copy
    # Ran 81 tests ... FAILED (failures=36, errors=6)  -> 42/81 red (51.9%), all mapping to the planted bugs / missing commands
.venv/bin/python -m pytest tests -q
    # 694 passed, 29 skipped, 49 subtests passed in 9.39s
just lint-imports
    # Contracts: 6 kept, 0 broken.
```

Pilot (stamp `20261104-033912`, dandy x3): 3/3 pass, judge 9.3/9.5/9.9 — archived at `/tmp/eval-pilot-033912-*`. Final matrix artifacts: `evals/runs/20261104-040318/{results.csv, report.md}` (gitignored; archive copies at `/tmp/eval-matrix-040318-*`). No commits made, per instruction.

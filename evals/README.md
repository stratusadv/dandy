# CLI eval harness

Compares four coding CLIs — **dandy** (this repo), **opencode**, **pi**, and
**crush** — on the same self-contained Terminal-Bench-style task with the same
model (`stratus.turbo`), measuring pass/fail (hidden tests), wall time, token
cost, and an LLM-judge diff-quality score. Every agent run executes inside an
ephemeral `docker run --rm` container; nothing is installed on the host.

## Layout

```
evals/
  docker/
    Dockerfile            # dandy-eval:latest — node:22-slim + git + python3
                          # + opencode-ai 1.19.5 + pi 0.73.1 + crush 0.99.0
                          # + stratus provider configs (baked)
    entrypoints/          # run inside each container
      common.sh           # copy task -> /workdir, git init, capture final diff
      dandy.sh            # one-shot dandy CLI via a localhost usage-logging proxy
      opencode.sh         # opencode run --format json
      pi.sh               # pi -p --mode json (stratus extension)
      crush.sh            # crush run (auto-executes tools)
      check.sh            # copy hidden tests in, export EVAL_TESTING=1, run unittest, tee check.log
  task/
    project/              # agent-visible: buggy stockroom CLI + TASK.md spec
    hidden_tests/         # 81 unittest cases; mounted only for the checker; skipped
                          # unless the EVAL_TESTING env var is set (the checker exports it)
    solution/             # reference implementation (never given to agents)
  harness/
    common.py             # docker runners, token parsers, cost, prompt
    run_eval.py           # orchestrator: matrix -> check -> judge -> report
    judge.py              # dandy JudgeBot (stratus.thinking) scores each diff
    report.py             # renders report.md
    usage_proxy.py        # 127.0.0.1:8787 proxy that logs dandy's real API usage
    dandy_settings.py     # eval settings: dandy -> usage proxy
    judge_settings.py     # eval settings: judge -> stratus.thinking
    clean.sh              # rm a run dir + kill labeled containers
  runs/<stamp>/           # gitignored; one dir per orchestrator invocation
  runs/archive/<stamp>/   # gitignored; results + per-run artifacts; survives clean.sh
```

## Prerequisites

- Docker with the daemon running.
- `AI_API_KEY` and `AI_API_HOST` exported in the environment (the stratus
  endpoint). The host needs no CLI installs — everything runs in the image.
- The dandy package is bind-mounted into containers at run time, so **no image
  rebuild is needed when dandy code changes**; the live working tree is what
  gets evaluated.

## Build

```bash
docker build -t dandy-eval:latest -f evals/docker/Dockerfile evals/docker/
```

## Run

```bash
# full matrix: 4 agents x 3 runs (agents in parallel, ~30 min cap per run)
.venv/bin/python evals/harness/run_eval.py --agents all --runs 3

# one agent only (pipeline smoke)
.venv/bin/python evals/harness/run_eval.py --agents dandy --runs 1

# skip the LLM judge
.venv/bin/python evals/harness/run_eval.py --agents all --runs 3 --no-judge
```

Use the repo venv python (`.venv/bin/python`) — the judge imports dandy and its
runtime deps. Results land in `evals/runs/<stamp>/`:

- `results.csv` — one row per run: pass, wall_s, tokens, cost_usd, agent_exit,
  timed_out, diff_stat, judge_total, note.
- `report.md` — aggregate table, per-run table, run detail (checker tail, judge
  scores/notes), caveats.
- `<agent>-run<n>/workdir/` — the agent's final tree plus `final.diff`,
  `final.diff.stat`, `transcript.log`, `agent.exit`, `check.log`, `judge.json`,
  and per-agent usage artifacts (`usage.jsonl` for dandy, `transcript.json` for
  opencode/pi, `.crush-data/crush.db` for crush).

At the end of every invocation the orchestrator copies `results.csv`,
`report.md`, and each workdir's small artifacts into
`evals/runs/archive/<stamp>/`, so `clean.sh` can never destroy results.

## Clean

```bash
evals/harness/clean.sh <stamp>   # removes evals/runs/<stamp> + labeled containers
```

Results and per-run artifacts are already archived in
`evals/runs/archive/<stamp>/` by the orchestrator, so cleaning is safe. Run
workdirs are pytest-ignored (`evals/conftest.py`), so leftover runs never
break `pytest evals` collection.

## Task

`task/project/TASK.md` specifies a `stockroom` JSON-inventory CLI over a
`(sku, location)`-keyed data model (add/remove/move/transfer/list/value/low/
summary/report/validate, exit codes 0/1/2). The shipped code is partway
through migrating from the legacy one-row-per-SKU model: six planted bugs
(add overwrites instead of merging, remove rejects full-quantity removals,
low-stock compares per-row counts instead of per-SKU totals, move appends a
duplicate row instead of merging, money rounding uses float `round()` instead
of Decimal half-up, remove accepts non-positive counts) plus four missing
commands (`transfer`, `summary`, `report`, `validate`). The 150-row seed
plants 4/5/6 count boundaries and X.XX5 rounding traps. The hidden tests
(81 cases) fail on a measured 42 of 81 on the pristine tree and pass with the
reference solution; an agent passes only if the hidden suite goes green.

Each agent run gets a 30-minute budget: each entrypoint wraps the agent
itself in `timeout -k 30 "${AGENT_TIMEOUT_SECONDS:-1800}"` (overridable via
env), and the orchestrator's outer `docker run` timeout adds a 240 s grace
period as a safety net for the entrypoint's post-agent diff capture, so a
budgeted-out agent still leaves `final.diff` and `agent.exit` (124) in its
workdir for the checker and judge. The LLM judge has a 300 s watchdog per
run; a judge that hangs or errors lands in the run's `note` and the run
continues.

To verify the reference solution without Docker, run the hidden suite in the
repo — `project/` is overlaid with `solution/` in a temp dir:

```bash
EVAL_TESTING=1 .venv/bin/python -m pytest evals -q   # 81 passed
```

Without `EVAL_TESTING` (or with it set to `0`), the hidden tests skip, so a
plain `pytest .` stays green.

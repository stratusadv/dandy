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
      check.sh            # copy hidden tests in, run unittest, tee check.log
  task/
    project/              # agent-visible: buggy stockroom CLI + TASK.md spec
    hidden_tests/         # 15 unittest cases; mounted only for the checker
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
# full matrix: 4 agents x 3 runs (agents in parallel, ~20 min cap per run)
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

## Clean

```bash
evals/harness/clean.sh <stamp>   # removes evals/runs/<stamp> + labeled containers
```

## Task

`task/project/TASK.md` specifies a `stockroom` JSON-inventory CLI (add/remove/
move/list/value/low + a missing `summary` command, exit codes 0/1/2). The
shipped code has four planted bugs (add overwrites instead of merging, remove
rejects full-quantity removals, value truncates cents, low-stock uses `<`
instead of `<=`). The hidden tests (15 cases) fail exactly on the buggy
behavior (8 failures on the pristine tree) and pass with the reference
solution; an agent passes only if the hidden suite goes green.

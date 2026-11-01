# CLI eval: dandy vs opencode vs pi vs crush

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-10-31-22-25

## End State
`evals/runs/<stamp>/report.md` exists: a comparison table of dandy, opencode, pi, and crush, each run 3x on the same self-contained Terminal-Bench-style task with the same model (stratus.turbo), showing per-run success (hidden-test pass/fail), wall time, token usage/cost, and an LLM-judge diff-quality score. Every agent run executes inside an ephemeral `docker run --rm` container built from a pinned eval image (nothing is installed on the host); cleanup of containers and run artifacts is a single command.

## Observable Concern
pi is the only agent whose headless path is unverified (not installed; its provider-config format and headless usage/cost reporting are unknown). If `@mariozechner/pi-coding-agent` cannot be pointed at the stratus endpoint or cannot report token usage headlessly, we deviate: estimate its tokens with dandy's own heuristic estimator (`dandy/domain/llm/tokens/utils.py`) over its session log, and say so in the report.

## Current State
Verified facts (2026-10-31):

- CLIs
  - dandy: not installed globally; it is this repo. One-shot mode: `python3 dandy/interfaces/cli/main.py "<prompt>"` (prints usage with `-h` before settings load). Coding model resolved via `CLI_CONFIG['CODING']` -> `LLM_CONFIGS`. Auto-creates `dandy_settings.py` if absent; harness must set `DANDY_SETTINGS_MODULE` + `PYTHONPATH` to an eval-owned settings module.
  - opencode 1.18.35 at `/home/nathanj/.opencode/bin/opencode`. Headless: `opencode run "<msg>" -m provider/model --dir <workdir> --auto --format json`. Already configured for stratus (`~/.config/opencode/opencode.jsonc`: openai-compatible, baseURL `${AI_API_HOST}:443/v1`, apiKey from env, per-model cost set).
  - crush 0.99.0 at `/usr/bin/crush`. Headless: `crush run "<prompt>" -m provider/model --cwd <dir> --yolo`; `--data-dir` pins the data dir per run; `crush stats` reports usage. Already configured for stratus (`~/.config/crush/crush.json`, openai-compat, pricing included).
  - pi: NOT installed. npm package confirmed: `@mariozechner/pi-coding-agent` v0.73.1. Install + config + usage-reporting to be verified in step 1 (inside the eval image, not on the host).
  - Docker: 29.9.2, daemon running, builder available, local images already buildable/pulled. stratus endpoint is plain HTTPS on 443, reachable from a container with network access.
- Model/API
  - stratus endpoint `https://ai.api.lc.ca.stratusadv.com:443`, OpenAI-compatible `v1/chat/completions`.
  - `stratus.turbo`: 48k context / 16k output, $1/$5 per Mtok, no thinking. `stratus.thinking`: 228k / 32k, $5/$25, xhigh effort.
  - Same-model decision: **stratus.turbo** for all four agents (cheap, fast, deterministic behavior class; 48k context is ample for the compact task). Budget for 12 runs + judging is well under ~$5.
- Environment
  - `development.env` carries `AI_API_KEY`/`AI_API_HOST`/`AI_API_PORT` + `LLM_*_MODEL` (all stratus). `DANDY_SETTINGS_MODULE` points at the test settings.
  - `.backplan/` exists. No `specs/` dir (evals is dev tooling, not a dandy feature, so no spec required). `setuptools` only packages `dandy*`, so `evals/` at the repo root cannot leak into the wheel.
  - Git identity: Nathan Johnson <nathanj@stratusadv.com>.

## Plan
1. <s>Install and smoke-test pi headlessly</s> (superseded by deviation 1)
   - <s>`npm i -g @mariozechner/pi-coding-agent`; configure it for stratus (same endpoint/key/model as the other three); run a trivial one-line prompt headlessly in a scratch dir; record its config file format, its permission/auto-approve behavior, and where it logs token usage.</s>
   - <s>Done when a headless pi prompt using stratus.turbo returns an answer and we know where its per-session token usage lives.</s>
1. Build the eval image and smoke-test pi inside it
   - `evals/docker/Dockerfile`: base `node:22-slim` + apt `git`; `npm i -g opencode-ai @mariozechner/pi-coding-agent`; crush via the official install script; `pip install pydantic requests blessed python-dotenv` (dandy's runtime deps only — the dandy repo itself is mounted read-only from the host at runtime, so dandy code changes never require a rebuild). Bake the stratus provider configs for opencode and crush (baseURL from `${AI_API_HOST}`) and the dandy settings module. The image is a runtime only: all eval code (task, harness, judges) lives in `evals/` in the repo and is mounted in.
   - First run inside a smoke container: verify stratus is reachable, run a trivial headless prompt through pi (record its config file format, auto-approve behavior, and where it logs per-session token usage), and confirm `timeout` + SIGTERM stops a `docker run` cleanly (the harness's 20-min cap relies on this).
   - Done when `docker build` succeeds, the smoke container answers a pi prompt on stratus.turbo, and we know where pi's per-run token usage lives.
2. Author the eval task
   - `evals/task/`: a small pure-stdlib Python project (CLI + 2-3 modules) with 3 planted bugs and 1 small missing feature, described in docs the agent can read; `evals/task/hidden_tests/` (unittest, hermetic, ~15 cases); `evals/task/check.sh` that copies the hidden tests in and runs `python3 -m unittest discover -v`; a reference solution kept out of the agent-visible copy.
   - Done when check.sh fails on the pristine copy and passes with the reference solution applied, proving the task is solvable and the checker correct.
3. <s>Build the per-agent launchers that spawn each CLI directly</s> (partially superseded by deviation 1)
   - <s>each spawns its CLI in a fresh workdir copy with the pinned model, a per-run timeout (20 min), and transcript capture; each also extracts token usage for its agent (opencode: `--format json` events; crush: pinned `--data-dir` session data / `crush stats`; dandy: recorder JSON of LLM responses' `usage` via an eval settings module; pi: whatever step 1 found, with dandy's token estimator as fallback).</s>
   - <s>Done when each launcher smoke-runs in a scratch workdir: process exits, transcript captured, tokens parsed for at least 3 of 4 agents.</s>
3. Build the per-agent docker-run launchers
   - `evals/harness/agents/{dandy,opencode,pi,crush}.py`: each spawns `docker run --rm --label dandy-eval=1 -e AI_API_KEY -e AI_API_HOST -e AI_API_PORT -v <run-dir>:/workdir -v $(pwd):/dandy:ro dandy-eval:latest <agent-entrypoint>`. The in-container entrypoint copies the task project into /workdir, `git init`s it, runs the agent CLI (pinned model, auto-approve flags, cwd=/workdir), then writes to /workdir: the transcript, a usage artifact (opencode: `--format json` events; crush: session data from a pinned data dir / `crush stats`; dandy: recorder JSON of LLM responses' `usage` via the eval settings module; pi: whatever step 1 found, with dandy's token estimator as fallback), and the final `git diff`. The host launcher measures wall time, enforces the 20-min cap with `timeout`, and on timeout kills the run and records it as a failure with the cause.
   - Done when each launcher smoke-runs once: container exits, artifacts land in the run dir, tokens parsed for at least 3 of 4 agents.
4. Build the orchestrator, judge, report, and cleanup
   - `evals/harness/run_eval.py`: builds the 4 agents x 3 runs workdir matrix (agents in parallel as separate containers, runs serial per agent), measures wall time, kills on timeout, runs check.sh per run in a short-lived container of the same image (`docker run --rm -v <run-dir>:/workdir dandy-eval:latest check.sh`) so the hidden tests execute in the same Python environment the agent coded in, collects `results.csv` (agent, run, pass, wall_s, input_tokens, output_tokens, cost_usd, notes).
   - `evals/harness/judge.py`: a dandy `JudgeBot` (stratus.thinking, runs host-side — it only reads diffs and never touches workdirs) scores each final `git diff` against the task statement + checker output on a 1-10 rubric (correctness, approach, code quality, no test-gaming) with written notes.
   - `evals/harness/report.py`: renders `report.md` (per-agent aggregate table + per-run detail + judge notes + caveats).
   - `evals/harness/clean.sh [stamp]`: removes any leftover `dandy-eval`-labeled containers and the `evals/runs/<stamp>` dir (transcripts are the eval's evidence, so cleanup is explicit, never automatic).
   - Done when `python3 evals/harness/run_eval.py --agents dandy --runs 1` completes the full pipeline (run -> check -> judge -> report) for one agent inside a container, and `clean.sh` leaves no labeled containers and no run dir (verified with `docker ps -a` and `ls`).
5. Run the full matrix
   - 4 agents x 3 runs = 12 runs against stratus.turbo; collect results.csv + report.md.
   - Done when all 12 runs have pass/fail, wall time, token/cost, and judge score rows; any timed-out or crashed run is recorded with its cause, not dropped.
6. Close the loop
   - Review report.md with the user; quote the checker output for each run into the report's evidence section; set this doc to Executed.
   - Done when the user has seen the report and this doc's status is Executed with the completion-test output quoted.

## Completion Test
`python3 evals/harness/run_eval.py --agents all --runs 3` exits 0 and produces:
- `evals/runs/<stamp>/results.csv` with exactly 12 data rows, every row having pass, wall_s, cost_usd, and judge_total filled (or an explicit error note), and
- `evals/runs/<stamp>/report.md` with the comparison table, and
- per-run checker transcripts at `evals/runs/<stamp>/<agent>-run<n>/check/check.log` whose actual pass/fail lines are quoted in the report, and
- `docker ps -a --filter "label=dandy-eval=1" -q` returns empty (no stray containers), and
- `evals/harness/clean.sh <stamp>` exits 0 and `evals/runs/<stamp>` is gone.

## Execution Record (2026-11-01)

Matrix stamp `20261101-202200` (`evals/harness/run_eval.py --agents all --runs 3`, under `.venv/bin/python`):

| agent | passed | wall (mean) | cost (total) | judge (mean) |
|---|---|---|---|---|
| crush | 3/3 | 69s | $0.0523 | 10.0 |
| pi | 3/3 | 65s | $0.1514 | 9.9 |
| opencode | 3/3 | 91s | $0.5223 | 10.0 |
| dandy | 1/3 | 440s | $10.9705 | 4.8 |

Per-run detail (pass / wall / cost / judge): crush 90.7s $0.017 10.0, 64.5s $0.018 10.0, 50.8s $0.017 10.0; pi 62.5s $0.045 10.0, 59.7s $0.052 9.8, 72.4s $0.055 10.0; opencode 138.0s $0.216 10.0, 84.1s $0.187 10.0, 51.6s $0.120 10.0; dandy 599.5s $5.188 2.5 (FAIL: 200-round cap, zero changes), 642.8s $5.635 2.0 (FAIL: 200-round cap, only `seed.json` mutated, code untouched), 77.0s $0.148 10.0 (PASS). All three dandy failures/loops show zero "Compacting" events — the compaction livelock fix held in every 200-round run; dandy's variance is stratus.turbo action-repetition (it passes in ~77s when it cooperates, as the Step-4 verification run did: 83.5s, $0.139, judge 9.3). Every passing run's diff is the same minimal root-cause shape (`add` merge, `remove` `>` vs `>=`, no `int()` truncation, `low` `<=`, `summary` added); the judge flagged no test-gaming in any run (the one `seed.json` mutation by dandy-run2 was caught and scored down to 2.0).

Completion test (all quoted from real output):
- `results.csv`: 12 data rows, every row with pass, wall_s, cost_usd, and judge_total filled (verified by script: "rows: 12 / all rows complete").
- `report.md` rendered the aggregate table above plus per-run detail; each run's checker line is quoted in it — 10x `OK | --- | CHECK_STATUS=0` and 2x `FAILED (failures=8) | --- | CHECK_STATUS=1` (dandy runs 1-2, where 8 failures is exactly the pristine-task baseline).
- `docker ps -a --filter "label=dandy-eval=1" -q` returned empty after the matrix (and again after cleanup).
- `evals/harness/clean.sh 20261101-202200` printed `removed evals/runs/20261101-202200`, exited 0, and the dir was gone. First invocation failed with rc=127 "permission denied" because `clean.sh` lacked the executable bit; fixed with `chmod +x` (the only other script in the harness needing this).
- Post-hoc repair (deviation 8): dandy-run1's in-run checker was skipped by the empty-`final.diff.stat` harness bug; the checker was re-run on its workdir (`Ran 15 tests ... FAILED (failures=8)`, `CHECK_STATUS=1`), the row's note corrected, and the report re-rendered.
- Evidence backup: `report.md`, `results.csv`, all 12 `check.log`/`final.diff`/`judge.json` files copied to `/tmp/eval-final-evidence/` before cleanup (38 files). The Step-4 verification run dir `evals/runs/20261101-201959` (pre-`.gitignore`, dandy pass 15/15 in 83.5s) was left in place.

## Deviations
1. Containerize all runs for easy cleanup
   - What: user required the eval to run inside a Docker container. Step 1 (host pi install) became "build the eval image" (all four CLIs installed in the image, dandy repo mounted read-only); step 3 launchers now wrap `docker run --rm` per run; step 4 gains `clean.sh`. Host installs of pi/opencode/crush are no longer needed (opencode/crush already exist on the host but the eval does not rely on them).
   - Why: user wants easy cleanup — ephemeral `--rm` containers plus one cleanup command leave no host or container residue.
2. Hidden-test checker moves from host-side into a throwaway container
   - What: step 4's check.sh now runs in `docker run --rm` from the same eval image instead of on the host.
   - Why: user confirmed everything test-related should run in containers; same-image check also guarantees the hidden tests run in the exact Python environment the agent coded in (no version-skew between agent env and checker env).
3. dandy token usage now measured by a localhost usage-logging proxy
   - What: the plan assumed dandy's recorder JSON carries LLM response `usage`; it does not (dandy never surfaces the API `usage` field, and recorder events store estimated tokens only). `evals/harness/usage_proxy.py` now proxies dandy's chat-completions calls locally (127.0.0.1:8787 -> stratus) and appends each real `usage` to the run dir's `usage.jsonl`. dandy's eval settings point at the proxy.
   - Why: dandy's cost must be real API usage like the other three agents, not an estimate.
4. crush session usage read from SQLite; `--yolo` not needed
   - What: crush stores sessions in `.crush-data/crush.db` (SQLite `sessions.prompt_tokens/completion_tokens`), so the parser uses the sqlite3 module instead of scanning session JSON. `crush run` in non-interactive mode executes tools without any approval flag (`--yolo` is rejected by the `run` subparser), so the launcher drops it.
   - Why: matches how crush v0.99.0 actually persists usage and handles permissions.
5. Eval image runs as the base image's `node` user
   - What: the image creates no new user; it runs as `node` (uid 1000 in node:22-slim, matching the host uid), with the stratus provider configs baked into `/home/node/.config`.
   - Why: files written into bind-mounted run dirs end up owned by the host user, so host-side cleanup and re-runs work without root.
6. The dandy working tree under test changed after approval
   - What: between approval and execution the repo's `v3/base` working tree moved to a newer v3 layout (`dandy/domain/llm/` split into `dandy/domain/{prompt,message,request,tokens}/`, `dandy/shared/conf/` -> `dandy/shared/settings/`, a new `dandy/application/agent/agent.py` `Agent` class, CLI gains `--continue`/auto-saved sessions). The harness was re-verified against the new layout: `docker_run_check()` was missing the `/entrypoints` bind mount (fixed in `evals/harness/common.py`), `judge.py`'s Prompt import moved to `dandy.domain.prompt.prompt`, and the dandy one-shot entrypoint was re-smoke-tested in-container on the new tree (SMOKE_OK in 2.4s, usage captured via the proxy). The host venv python is now the only python with dandy's runtime deps, so the judge/orchestrator run under `.venv/bin/python`.
   - Why: the dandy package is bind-mounted into every container at run time, so the code under test is whatever the live working tree holds; the harness must track it.
7. Fix dandy's compaction livelock before the matrix (user-directed, 2026-11-01)
   - What: before step 5, dandy's current code must be fixed. Observed twice in-container (and by the user in interactive CLI use): on the stockroom task the agent livelocks for the full 20-min cap — ~551 LLM rounds of tiny tool calls (repeatedly `run_command("echo done")`), ~10.7M input tokens (~$10.80), zero code changes, 0/15 tests — while "Compacting conversation history (33635 tokens)..." repeats every round with the count pinned at the 70% target. Root causes found: (a) the CLI turn and the planning phase run the tool loop with `max_tool_iterations=None`, so a model stuck in tool-call-only mode never gives up; (b) tool-loop and pre-turn compaction trigger exactly at the 0.70 target with no hysteresis, so a steady state (each round re-adding about what compaction just dropped) re-compacts every round; (c) the token estimator runs ~1.3x hot vs the API count, so compaction sheds context while the real 48k window is only ~59% used. Fix (in `dandy/application/agent/agent.py`, `dandy/application/agent/coding_agent.py`, `dandy/application/agent/prompts.py`, `dandy/application/tool/service.py` + tests): compaction hysteresis (trigger 0.80, compact down to 0.70), `AGENT_MAX_TOOL_ROUNDS_DEFAULT = 100` cap on agent turns and the planning phase (pass `max_tool_rounds=None` to opt out), and a final-answer line in the coding guidelines ("stop calling tools and respond with your final answer as plain text").
   - Why: user said "we keep it the 12 runs but we need to fix dandy's broken compaction looping, it happened when I use the cli". A $10.80-per-run livelock would also break the matrix budget (~$5) and would not be a fair eval of dandy's coding ability.
   - Verified when: hermetic tests pass (`test_agent_turn_caps_tool_rounds`, hysteresis band tests in `test_coding_agent.py`/`test_service.py`), and a fresh in-container stockroom run either passes the hidden tests or fails fast with the 100-round error instead of the 20-min/$10 spin.
   - Addendum (first verification round): the 100-round cap worked (run failed fast at 101 LLM calls, $1.47, clear "gave up after 100 tool iterations" error) and hysteresis worked (zero "Compacting" events in 101 rounds, previously every round), but stratus.turbo's workflow on this task is round-heavy: it spent all 100 rounds *verifying* the planted bugs against `seed.json` (exit codes, git-checkout restore between tests) and never reached the editing phase. That is structurally unfair in the eval, so the cap was raised to `AGENT_MAX_TOOL_ROUNDS_DEFAULT = 200` (covers reproduce-then-fix-then-verify at the observed ~22 rounds/min, still well inside the 20-min wall cap, and bounds the degenerate loop to ~9 min/~$5 instead of 20 min/$10.80).
   - Addendum (final verification, dandy6 run, 200 cap): the framework fix holds end-to-end — zero "Compacting" events across the whole run (prompt grew 1,856 -> 32,821 tokens, never near the 0.80 trigger of ~52,428), and the run stops at exactly 200 tool iterations with the clear "LLM Tool Service gave up after 200 tool iterations without a final response." error. Wall 7m21s, 201 LLM calls, 3,958,779 in / 15,843 out = $4.04, checker 0/15 (8 failures, identical to the pristine baseline). The remaining failure is model behavior, not the framework: stratus.turbo read everything, probed the CLI, computed the expected values (33 `python3 -c` rounds), then fell into an action-repetition loop re-running the same `value A1; value B2; value C3` command ~130 times without ever calling `edit_file`/`write_file` (verified: no edit beats in the transcript, and prompt-token growth per round shows tool results were reaching the model). Dandy's honest eval result is therefore a fast, bounded round-cap failure on this model; the compaction livelock itself (the user-reported bug) is fixed.
8. Harness diff-capture fixes found while the matrix was running (2026-11-01)
   - What: (a) added `evals/task/project/.gitignore` covering harness-written runtime artifacts (transcripts, usage logs, pycache, `.crush-data/`, `.pi-sessions/`, `agent.exit`, `final.diff*`, `check.log`, `judge.json`, `inventory.json`) so `final.diff` contains only the agent's own changes; (b) fixed `diff_stat()` in `evals/harness/common.py` to return `''` when `final.diff.stat` is empty instead of raising `list index out of range`.
   - Why: (a) the entrypoints write their artifacts into the agent's git worktree and `capture_final_diff` does `git add -A`, so harness noise landed in every agent's diff and the judge docked quality for it (the Step-4 verification run scored quality 7 for that reason; with the ignore file, diffs are just `2 files changed, ~14 insertions(+), 4 deletions(-)`); (b) a run where the agent changed nothing produces an empty stat file, and the IndexError aborted the row before the checker ran (matrix dandy-run1: correct pass=False but no `check.log` and a misleading note) — repaired post-hoc by running the checker and judge on that workdir and re-rendering the report.

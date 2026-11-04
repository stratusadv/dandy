# Remove per-turn planning

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-03-20-59

## End State

`CodingAgent` sends every turn straight to the coding bot: `dandy/application/agent/bots/planning_bot.py` is deleted, `planning_guidelines_prompt` is gone, `CodingAgent.__init__` no longer accepts `run_planning`, `grep -rn -i "planning" dandy/` (excluding `__pycache__`) returns nothing, a mocked hermetic turn makes exactly one LLM HTTP request and emits no 'Planning' beat, and the hermetic suite, `ruff check`, `ruff format --check`, `just lint-imports`, and `just docs-tests` (strict mkdocs build) all pass, plus the live `just repl-smoke` runs clean with no 'Planning' beat.

## Observable Concern

The mkdocstrings directive in `docs/reference/application.md` points at the deleted `PlanningBot`, so the class deletion, the directive deletion, and the test updates (`CodingAgent(run_planning=False)` appears ~10 times in `test_coding_agent.py` plus 3 times in `test_init_bot.py`) must land together — any partial removal leaves the strict docs build or the hermetic suite red.

## Current State

- **The per-turn planning pass** (`dandy/application/agent/coding_agent.py:32`, `_prepare_message`): on every turn it resets `PlanningBot` (fresh conversation each time, by design), emits a `StoryBeat(description='Planning')`, runs a full tool loop with the complete `AGENT_TOOLS` — including `write_file`/`edit_file`/`delete_file`/`run_command` — on the THINKING-config model capped at `AGENT_MAX_TOOL_ROUNDS_DEFAULT` (200) rounds, and folds the result into the user message under an `Implementation Plan` heading.
- **It runs unconditionally in the CLI**: `run_planning: bool = True` is the default (`coding_agent.py:23`) and `DandyCli` builds `CodingAgent(ask_user=...)` (`dandy/interfaces/cli/cli.py:42`), so every REPL turn, one-shot `dandy "<request>"`, and `--continue` turn pays for it. There is no CLI command, settings key, or CLI_CONFIG entry to turn it off.
- **Continuation turns re-plan too**: `Agent.run` calls `turn(continuation_prompt())` (`agent.py:184`), and the coding agent's `_prepare_message` plans that "keep going" nudge as well.
- **Stale plans persist**: the injected `Implementation Plan` section lives in the persisted `MessageHistory`, so later turns of a conversation carry plans written for earlier requests.
- **A planning failure kills the turn**: `_create_plan` has no error handling; a provider error surfaces at the CLI as `Coding agent failed` (`cli.py:220`) even for a trivial request the coding bot could handle alone.
- **Dead code**: `PlanningBot.process` (`planning_bot.py:36`) is never called and omits `intel_class` in its `prompt_to_intel` call.
- **Production references are contained**: `dandy/application/agent/bots/__init__.py` is empty; the only planning references in `dandy/` are `coding_agent.py`, `planning_bot.py`, and `planning_guidelines_prompt` (`prompts.py:196`). `AGENT_MAX_TOOL_ROUNDS_DEFAULT` stays — `run_init_pass` still uses it.
- **Tests**: `TestCodingAgentPlanning` (`tests/application/agent/test_coding_agent.py:569`, 4 tests: plan feeding, skip-when-disabled, no give-up after 5 rounds, fresh conversation); `CodingAgent(run_planning=False)` in ~10 places in `test_coding_agent.py` and 3 in `test_init_bot.py`; `test_compaction_counts_the_plan_section_of_the_prompt` (`test_coding_agent.py:497`) uses a plan-shaped long prompt as its fixture.
- **Docs that describe the planning pass**: `docs/user_guide/coding_agent.md` (pipeline diagram step 1 + the "planning pass is an override of the base `_prepare_message` hook" paragraph), `docs/architecture/agents.md` (The CodingAgent section, the four-bot table, the "CodingBot and PlanningBot fold AGENTS.md" sentence), `docs/reference/application.md` (the `PlanningBot` mkdocstrings directive), `AGENTS.md` (the agent bullet's `_prepare_message`/planning sentence and the CLI bullet's PlanningBot mentions), and `docs/changelog/v3.md` (a v3.1.0 `Changed` entry describing the planning hook, lines 162–171; a `### Removed (breaking)` subsection exists at line 231).
- **Live smoke is safe**: `scripts/repl-smoke.sh` has no planning expectation; `development.env` exists, so `just repl-smoke` (two scripted live REPL sessions) can run as the vision check. The `evals/runs/*/transcript.log` files show the 'Planning Evaluating ...' spam but are historical artifacts, not test inputs.

## Plan

1. Remove planning from `CodingAgent`
   - Edit `dandy/application/agent/coding_agent.py`: drop the `run_planning` parameter (signature becomes `__init__(self, ask_user: QuestionHandler | None = None)`), `self.run_planning`, `self.planning_bot`, the `_prepare_message` and `_create_plan` overrides, `self.planning_bot.reset()` from `clear()`, and the `PlanningBot` import.
   - Done when the module imports cleanly, has no planning references, and `ruff check` on it is clean.
2. Delete `PlanningBot` and the planning prompt
   - Delete `dandy/application/agent/bots/planning_bot.py`; delete `planning_guidelines_prompt` from `dandy/application/agent/prompts.py`.
   - Done when `grep -rn -i "planning" dandy/` (excluding `__pycache__`) returns nothing.
3. Update the tests
   - Delete the `TestCodingAgentPlanning` class; replace every `CodingAgent(run_planning=False)` with `CodingAgent()` in `test_coding_agent.py` and `test_init_bot.py`; repurpose `test_compaction_counts_the_plan_section_of_the_prompt` as a generic long-incoming-prompt compaction test (rename, keep the mechanism).
   - Done when `just test` passes and `grep -rn "run_planning" tests/` returns nothing.
4. Update docs and changelog
   - `docs/user_guide/coding_agent.md`: drop pipeline step 1, renumber, rewrite the "CodingAgent is the framework's own child of the base Agent" paragraph (no `_prepare_message` override; the turn is inherited unchanged).
   - `docs/architecture/agents.md`: rewrite the CodingAgent section (no planning pass; `CodingAgent` is the plain `Agent` child with the question tool), bot table 4 -> 3 rows, "Four `Bot` subclasses" -> "Three", AGENTS.md folding sentence -> `CodingBot` only.
   - `docs/reference/application.md`: remove the `PlanningBot` directive.
   - `AGENTS.md`: rewrite the agent bullet (drop the `_prepare_message`/planning sentence) and the CLI bullet (drop `PlanningBot` from the bot list and the AGENTS.md-folding sentence).
   - `docs/changelog/v3.md`: strip the planning description from the v3.1.0 `Changed` entry (lines 162–171) and add a `Removed (breaking)` entry recording that the per-turn planning pass, `PlanningBot`, and `run_planning` never shipped and are removed — turns go straight to the coding bot.
   - Done when `grep -rn "PlanningBot\|Implementation Plan" docs/ AGENTS.md` returns only the changelog Removed note and `just docs-tests` passes.
5. Verify hermetic, then live
   - Run `just test`, `ruff check .`, `ruff format --check .`, `just lint-imports`, `just docs-tests`; then the live `just repl-smoke`.
   - Done when every command exits 0 and the smoke transcript shows no 'Planning' beat with both scripted sessions succeeding.

## Completion Test

```
just test                       # hermetic suite green (mocked turn = 1 HTTP request, no 'Planning' beat)
ruff check . && ruff format --check .
just lint-imports               # DDD contracts hold
just docs-tests                 # strict mkdocs build (catches the stale PlanningBot directive)
just repl-smoke                 # live two-session REPL smoke via development.env creds
grep -rn -i "planning" dandy/   # no matches outside __pycache__
```

## Deviations

1. `just test` (broad `pytest .`) is unusable as the hermetic gate.
   - What: ran the CI-equivalent hermetic suite instead — `pytest tests -q` and
     `python -m unittest discover -t . ./tests` (both with
     `DANDY_SETTINGS_MODULE=tests.dandy_settings`, `AI_API_KEY=placeholder`).
   - Why: today's `evals/runs/*/workdir/tests/` harness directories (gitignored
     local artifacts) contain a `tests` package that shadows the repo's `tests`
     package, so any `pytest .` collection dies with 107 import errors. The
     failure reproduces identically on pristine HEAD, so it is pre-existing
     local pollution, not a regression; CI's hermetic job scopes to `./tests`,
     which is what was run.
2. `ruff check .` was not clean at HEAD, so "ruff clean" could not be the gate.
   - What: verified the working tree's ruff findings are byte-identical to
     HEAD's (same 798 findings), after fixing the one TC001 my edit introduced
     (`StoryBeat` in `coding_agent.py` moved to a `TYPE_CHECKING` block once it
     became annotation-only). `ruff format --check` drift (15 files) was also
     confirmed pre-existing and none are files touched here.
   - Why: the `.venv` ruff is 0.17.3, newer than the version that last
     linted/formatted the repo, so it fires hundreds of pre-existing findings.
     Repo-wide tool-drift cleanup is out of scope for this change.

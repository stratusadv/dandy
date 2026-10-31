# Base Skill class: prompt + methods, registered on Bots and Agents

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed (user sign-off: "yes")
- Date: 2026-10-30-22-10

## Research (industry precedent)

**Verified primary source — Anthropic Agent Skills docs
(platform.claude.com/docs/en/agents-and-tools/agent-skills/overview, fetched
2026-10-30):**
- "Skills are reusable, filesystem-based resources that give Claude
  domain-specific expertise: workflows, context, and best practices..."
- Three-tier progressive disclosure: Level 1 metadata (`name` + `description`,
  ~100 tokens, always loaded at startup); Level 2 instructions (the SKILL.md
  body, loaded when the skill is triggered); Level 3+ resources (loaded on
  access).
- Verbatim: "Claude loads this metadata at startup and includes it in the
  system prompt. The `description` is what Claude matches your request against
  when determining whether to trigger the Skill."
- Activation has **no dedicated tool**: the model matches the request against
  the description, then reads SKILL.md itself via bash — "Only then does this
  content enter the context window." Bundled scripts are *executed* via bash
  and "only its output ... consumes tokens" (never the code).
- Frontmatter requires `name` and `description`; the description "must include
  both what the Skill does and when Claude should use it."

**Converging context (established API knowledge, not re-fetched):**
- MCP: a server bundles tools + prompts + resources; server prompts are
  first-class reusable templates. The "prompt + callables bundle" shape is
  standard; selection is client-driven.
- Semantic Kernel: "plugins" are collections of functions; prompt templates
  are a separate concept. No first-class prompt+functions bundle.
- Pydantic AI / LangChain / CrewAI: tools only; no first-class skill concept.
- The name "skill" is currently dominated by the Anthropic usage. Dandy's
  version is the code-first equivalent: a Python class (prompt attribute +
  typed methods) instead of a SKILL.md directory, and a first-class
  `activate_skill` tool instead of a bash `cat` — the same information flow
  (metadata in system prompt, full instructions enter context as a tool
  result, callable code executed not read), minus the filesystem.

## End State

`from dandy import BaseSkill` works, and a skill (a prompt plus explicitly
declared methods) can be registered **active** (its prompt is in the system
message on every request and its methods are always tools) or **passive**
(name + description in the system message; the model calls the built-in
`activate_skill` tool, the skill's prompt then enters the context as a tool
result, and its methods join the tool list) — on a `Bot` (class attribute)
or an `Agent` (constructor param) — with the full gate battery green and the
published docs explaining the concept.

## Observable Concern

The risky part is mid-loop tool-list mutation: a passive skill's methods must
appear in the request only *after* the model's `activate_skill` round, so the
per-request `tools` array grows across one conversation. Providers must
accept that, and every `role='tool'` result must reference a tool that is
defined in the same request. The design enforces monotonicity — activation is
one-way until `clear()`/reset, the `activate_skill` tool is present while any
passive skill is unactivated, and the system message is written once and never
rewritten. If a live strict endpoint (CI's vLLM via litellm) 400s on the
growing tools array, the design is wrong and must be revisited (fallback:
declare all skill tools from round 1 and gate only the instructions).

## Current State (verified 2026-10-30)

- `BaseTool` (`dandy/domain/tool/tool.py`): ABC; `name`/`description` class
  attrs; abstract `handle(**kwargs)` whose typed signature becomes the
  parameter schema (`IntelFactory.callable_signature_to_intel_class` on the
  bound method, cached per instance); `action_sentence`; `to_function_dict`;
  `run_subprocess` helper; `ToolType = type[BaseTool] | BaseTool` and
  `to_tool_instances()` normalize classes/instances.
- `ToolService` (`dandy/application/tool/service.py`):
  `prompt_to_intel(prompt, intel_class, ..., tools, tool_functions,
  max_tool_iterations=5, progress_callback, verbose_callback, **kwargs)`; the
  loop currently builds `tool_instances`/`tools_by_name` **once before** the
  `while True`, and each round calls `self.obj.prompt_to_intel(tools=tool_instances, ...)`;
  `_process_tool_call` validates args against the tool schema, emits the
  action sentence, dispatches `tool.handle(**kwargs)` (an external
  `tool_functions[name]` wins), and appends `role='tool'` to
  `self.obj.messages`.
- `LlmService` (`dandy/application/llm/service.py`): `__post_init__` builds
  `LlmConnector(system_prompt=service_system_prompt(role, task, guidelines,
  system_override_prompt).to_str(), ...)` — the system prompt is built once,
  at first `.llm` access; bases are `BaseService, DecisionServiceMixin,
  DiligenceServiceMixin, ToolServiceMixin`; precedent: `__post_init__` already
  creates sibling services mid-init (`self.diligence.post_handler`);
  `reset()` resets connector + messages and calls no `super().reset()`.
- `LlmServiceMixin` (`dandy/application/llm/mixin.py`): the bot's class-attr
  config surface (`llm_config`, `intel_class`, `role`, `task`, `guidelines`,
  `system_override_prompt`); `llm` property lazily builds
  `LlmService(obj=self)`; `reset()` → `self.llm.reset()`.
- `ToolServiceMixin` (a base of `LlmService`, not of `Bot`) gives
  `bot.llm.tools` → `ToolService(obj=LlmService)` — the exact shape
  `SkillServiceMixin` mirrors (`bot.llm.skills`).
- `LlmConnector` (`dandy/infrastructure/llm/connector.py`):
  `system_prompt_str` is static after init; `_prepend_system_message()`
  prepends only when the merged history has no system message; `tools` are
  set per request (`request_body.tools = [t.to_function_dict() ...]`) and
  `response_format` is cleared whenever tools are present.
- `Agent` (`dandy/application/agent/agent.py`):
  `Agent(bot, tools=None, max_turns=None, intel_class=None)`; `turn` →
  `bot.llm.tools.prompt_to_intel(..., max_tool_iterations=None,
  message_history=self.history, replace_message_history=True)`; `run` drives
  turns; `clear()` = new history + `bot.reset()`.
- `Bot` (`dandy/application/bot/bot.py`): `process(*args, **kwargs)` forwards
  `prompt` + kwargs to `self.llm.prompt_to_intel`; subclass configuration is
  via class attributes — the established bot config surface.
- `BaseServiceMixin._get_service_instance(ServiceClass)` lazily builds
  `ServiceClass(obj=self)` and caches it on `_{name}_instance`.
- No "skill" concept exists anywhere in `dandy/` or `tests/` (grep-verified).
- Baselines after the Agent feature (2026-10-30): pytest `456 passed, 29
  skipped`; unittest `Ran 485` / `OK (skipped=29)`; coverage `TOTAL 94%`
  (gate 90); `lint-imports` `Contracts: 6 kept, 0 broken.`; `just docs-tests`
  exit 0; `ruff check .` 648 errors; `ruff format --check .` 155 files.

## Proposed API (for approval)

```python
from dandy import BaseSkill


class GitSkill(BaseSkill):
    name = 'git'
    description = 'Work with the git repository: status, diffs, history.'
    prompt = (
        'You are working inside a git repository. Run read-only git '
        'commands before making changes and never force-push.'
    )
    active = False  # passive: the model activates it
    tools = ['status', 'diff']  # these methods become tools

    def status(self) -> str:
        """Show the working tree status."""
        return self.run_subprocess(['git', 'status'])  # if it wants shell

    def diff(self, staged: bool = False) -> str:
        """Show the diff of unstaged (or staged) changes."""
        ...
```

- `BaseSkill` (`dandy/domain/skill/skill.py`): class attrs `name`,
  `description`, `prompt`, `active: bool = True`, `tools: list[str] = []`
  (method names); `__init__(self, active: bool | None = None)` so a class can
  be flipped per instance (`GitSkill(active=False)`); `get_method(name)`
  validates a declared method exists, is public, and is callable;
  `SkillType = type[BaseSkill] | BaseSkill`, `to_skill_instances()`.
- Generated tool names: `{skill.name}_{method}` (e.g. `git_status`); tool
  description = first docstring line of the method (fallback: the name).
- `SkillService` (`dandy/application/skill/service.py`, via
  `SkillServiceMixin` on `LlmService` → `bot.llm.skills`):
  - `register(skills)` — normalize, validate (name/description required;
    passive skills must have a description; unique skill names; generated
    tool names unique and not `activate_skill`), store.
  - `system_prompt_section() -> str` — active skills: full prompt under a
    heading per skill; passive skills: a one-paragraph instruction plus a
    `- name: description` list. Built once at registration; never rewritten.
  - `active_tools() -> list[BaseTool]` — method tools for active skills plus
    method tools for activated passive skills; plus the synthetic
    `activate_skill` tool while any passive skill is unactivated.
  - `activate(name) -> str` — the `activate_skill` handler: unknown name →
    "No skill named X. Available passive skills: ..."; already active →
    "already active" note; success → marks active and returns the skill's
    prompt text (the tool result, so the instructions enter context exactly
    like Anthropic's `cat SKILL.md`).
  - `reset()` — clears activated passives (called from `LlmService.reset()`).
- `LlmServiceMixin` gains the `skills: list[SkillType] = []` class attribute
  (the Bot-level registration surface, alongside `role`/`task`/`guidelines`).
  `LlmService.__post_init__` registers `self.obj.skills` and appends
  `system_prompt_section()` to the built system prompt.
- `LlmService.append_system_prompt(section)` — appends to
  `system_prompt_str`; used by `Agent` so agent-registered skills reach the
  system message after the bot's was already built (only valid before the
  first turn, documented).
- `ToolService.prompt_to_intel` — inside the loop, each round:
  `round_tools = user_tools + skill_service.active_tools()`; a fail-fast
  `LlmCriticalError` if a user tool name collides with a skill tool name.
  Dispatch, validation, action sentences, `tool_functions` override, and the
  recorder all work unchanged (skill tools are plain `BaseTool` instances).
- `Agent.__init__(bot, tools=None, skills=None, max_turns=None,
  intel_class=None)` — registers skills on `bot.llm.skills` and appends the
  section; `Agent.clear()` (via `bot.reset()`) de-activates passives.
- Exceptions: `SkillCriticalError(DandyCriticalError)`
  (`dandy/domain/skill/exceptions.py`). No recoverable variant in v1.
- Root-exported: `BaseSkill` only (`Agent`/`Bot`/`BaseTool` stay the
  registration surfaces; `SkillService` is reachable via `bot.llm.skills`).
- **No new import-linter seams**: `domain/skill` is imported by
  `application/skill` and `application/agent` (application → domain);
  `LlmService`/`ToolService` touch skills through `self.obj.skills`
  (application → application). The 6-contract battery stays as-is.

## Assumptions (flagged for approval)

1. Generated tool names are `{skill.name}_{method}`; no per-method override in
   v1 (easy follow-up).
2. The activation mode is the skill's `active` attr (class-level, overridable
   at instantiation). There is no per-call "register as active" — a skill is
   one mode for the lifetime of its registration.
3. Activation is one-way within a conversation: no de-activation until
   `clear()`/`reset()`; once all passives are active, `activate_skill`
   disappears from the tool list.
4. The skill section of the system prompt is static per conversation (built
   at registration, never rewritten) — the passive metadata list stays visible
   even after activation (harmless; rewriting the system message would break
   strict endpoints and Dandy's prepend-once behavior).
5. Bot-level skills are a class attribute on the Bot subclass (the established
   bot config surface); a `Bot(skills=[...])` constructor kwarg is not
   documented (setattr ordering vs. first `.llm` access is not reliable).
6. Agent-registered skills live on the underlying bot's `LlmService`, so two
   Agents sharing one Bot share the registry — use separate Bots for separate
   skill sets (documented).
7. The `activate_skill` tool result is the skill prompt text with a one-line
   header; the model is instructed (in the system section) to treat the result
   as instructions to follow.
8. Prompt-only skills (no `tools`) are legal; a skill with an empty `prompt`
   activates with a "no additional instructions" note.
9. `tools` is a list of method-name strings; no `handle_`-prefix convention.
10. File-based skill discovery (`.dandy/skills/`) is explicitly out of scope
    for v1 (user decision).

## Plan

1. **Domain package** — `dandy/domain/skill/{__init__,skill,exceptions,prompts}.py`
   (BaseSkill, SkillType, to_skill_instances, get_method, SkillCriticalError,
   `skill_system_prompt_section`) + `tests/domain/skill/test_skill.py`.
   - Done when: base-class unit tests pass (normalization, method resolution,
     name/description validation, section text for active+passive) under both
     pytest and unittest.
2. **Application service** — `dandy/application/skill/{__init__,service,mixin,tools}.py`
   (SkillService, SkillServiceMixin, SkillMethodTool, ActivateSkillTool),
   `LlmServiceMixin.skills` class attr, `LlmService` wiring (mixin base,
   register + section in `__post_init__`, `append_system_prompt`,
   `skills.reset()` in `reset()`), plus skill fakes in
   `tests/application/skill/intelligence/skills.py` and
   `tests/application/skill/test_service.py`.
   - Done when: SkillService tests pass (register/validate/section,
     active_tools growth, activate() flows, reset, collision errors) and the
     full suite is still green.
3. **Tool-loop integration** — per-round `round_tools` in
   `ToolService.prompt_to_intel` + user/skill name-collision guard; hermetic
     loop tests in `tests/application/tool/test_service.py` (or a new
     `tests/application/skill/test_tool_loop.py`).
   - Done when: a mocked `request_to_response` sequence proves (a) an active
     skill's methods are on the wire from round 1 with its prompt in the
     system message, (b) a passive skill's `activate_skill` call returns its
     prompt as a tool result and its methods appear from the next round,
     (c) a colliding user tool raises `LlmCriticalError` before any HTTP call.
4. **Agent surface** — `Agent(skills=...)` param + registration in
   `__init__`; `tests/application/agent/test_agent_skills.py` (metadata in the
   first turn's system message; activation persists across turns; `clear()`
   de-activates).
   - Done when: the agent skill tests pass under both runners and
     `Agent(bot, tools=..., skills=...)` smoke-imports cleanly.
5. **Public API + fakes audit** — `BaseSkill` in `dandy/__init__.py` +
   `__all__`; verify `from dandy import BaseSkill` from a clean interpreter;
   confirm the reset-chain test still passes (the skill service must not
   break `tests/application/bot/test_reset_chain.py`).
   - Done when: the smoke import works and the reset-chain test is green.
6. **Docs** — new `docs/user_guide/skill.md` (concept, active/passive table,
   worked example, the activation flow, Bot + Agent registration, naming and
   collision rules, description-writing guidance, relationship to tools and
   agents) + `mkdocs.yml` nav entry (after Tool Calling);
   `docs/reference/domain.md` (BaseSkill, SkillType, to_skill_instances,
   SkillCriticalError) and `docs/reference/application.md` (SkillService);
   `docs/domain_model/glossary.md` (Skill entry + anti-language rows);
   `docs/changelog/v3.md` Added bullet; `AGENTS.md` (new `### Skill` section
   after `### Agent`, tool-calling section mention, public-API list, testing
   line).
   - Done when: `just docs-tests` strict build is clean.
7. **Completion test + close** — run the full battery below, quote real
   output, append deviations, set `Status: Executed`.
   - Done when: every completion-test line passes.

## Completion Test

All run from `/home/nathanj/PycharmProjects/dandy`, all must pass (N = new
hermetic test count; baselines in Current State):

1. Hermetic pytest:
   `AI_API_KEY=test-key PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -m pytest . -q`
   -> 456+N passed, 29 skipped, 0 failed.
2. CI-parity unittest (clean env):
   `env -i PATH="$PATH" HOME="$HOME" .venv/bin/python -m unittest discover -t . ./tests`
   -> 485+N tests, 0 failures, 29 skipped.
3. Coverage gate:
   `PYTHONPATH=. AI_API_KEY=placeholder DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -m coverage run -m unittest discover -t . ./tests && .venv/bin/python -m coverage report --fail-under=90`
   -> TOTAL >= 90%, exit 0.
4. Architecture: `.venv/bin/lint-imports` -> `Contracts: 6 kept, 0 broken.`
   (no new seams expected — see Proposed API).
5. Docs: `just docs-tests` -> strict mkdocs build clean.
6. Style: `.venv/bin/ruff check .` <= 648 errors; `.venv/bin/ruff format --check .`
   reformat count <= 155 (format new files before the final count; ruff
   formats markdown code fences, so the plan doc and new docs pages included).
7. API smoke:
   `PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -c "from dandy import BaseSkill; s = type('S', (BaseSkill,), {'name': 'x', 'description': 'd', 'prompt': 'p'}); print(s())"`
   -> prints an `S` instance, exit 0.
8. Activation wire assertion (inside step 3's tests): after the
   `activate_skill` round, the next request body's `tools` array contains the
   skill's method tools and the `role='tool'` message contains the skill's
   prompt text.
9. Optional live smoke (only with a real `development.env` key, like the
   earlier live evaluations): a small passive skill with one tool, `run()` a
   task that should trigger it, assert the model called `activate_skill` then
   the skill tool — reported separately, not a gate.

## Deviations

1. **Per-round request capture in the wire tests (steps 3 and 4)** — What: the
   plan's loop tests read the mocked `request_to_response` arguments by call
   index (`call_args_list[i].kwargs['request_intel']`). In practice
   `LlmConnector` mutates and reuses one `request_body` object across rounds
   and passes it by reference, so every index pointed at the same object in its
   *final* loop state (round 1's tools array read as the post-activation array,
   initially masquerading as a product bug — a probe confirmed
   `SkillService.active_tools()` and the `tools` argument reaching
   `LlmService.prompt_to_intel` were correct per round). Fix: the wire tests
   (`tests/application/skill/test_tool_loop.py`,
   `tests/application/agent/test_agent_skills.py`) install a `side_effect`
   callable (`make_fake_request_to_response`) that deep-copies
   `request_intel.json_data` at call time and serves queued responses, so each
   round is asserted against its own snapshot. No product code changed; the
   system/user message `content` arrives on the wire as a list of
   `{'type': 'text', ...}` parts, which the test helpers join before
   asserting. All step 3/4 "done when" wire assertions pass unmodified against
   the snapshots.

## Execution Report

N = 46 new hermetic tests (18 `tests/domain/skill/test_skill.py`, 24
`tests/application/skill/` — 20 service + 4 loop, 4
`tests/application/agent/test_agent_skills.py`).

1. Hermetic pytest:
   `502 passed, 29 skipped in 3.91s` (456 + 46).
2. CI-parity unittest (clean env):
   `Ran 531 tests in 3.475s` / `OK (skipped=29)` (485 + 46).
3. Coverage gate: `TOTAL  4226  253  94%`, `--fail-under=90` exit 0.
4. Architecture: `Contracts: 6 kept, 0 broken.` (no new seams).
5. Docs: `just docs-tests` exit 0 (strict mkdocs build clean).
6. Style: `Found 648 errors.` (baseline 648);
   `155 files would be reformatted, 266 files already formatted`
   (baseline 155; new files and the new docs page formatted).
7. API smoke: prints `<__main__.S object at 0x7fdc72bf44d0>`, exit 0.
8. Activation wire assertion:
   `tests/application/skill/test_tool_loop.py::TestPassiveSkillActivationInToolLoop::test_passive_skill_activated_mid_loop`
   passes — the request after the `activate_skill` round carries
   `weather_current` in `tools` (no `activate_skill`), and the
   `role='tool'` message carries the skill's prompt text
   ('Answer weather questions using the weather tool.').
9. Optional live smoke: not run (no live key was exercised this session);
   offered after close-out.

# Application Layer

The application layer orchestrates: it composes domain objects with infrastructure to
execute use cases. `Bot` is the entry point; the LLM, tool, decision, and diligence
services are the use-case services that hang off it; `Agent` is the stateful, looped
generalization of a Bot; the coding agent is the framework's own in-house use case
(the CLI's brain).

The application layer may depend on the [domain](domain.md) and the
[shared kernel](shared.md). It is allowed to depend on the [infrastructure layer](infrastructure.md)
at the seams documented in [Layering and Dependency Rules](../architecture/layering.md)
(services need to build their connectors), but no other cross-layer imports are allowed.

## Bot

The composition root for end users: `Bot` wires the file, LLM, HTTP, and Intel services
together and provides `process` (with automatic [recording](../user_guide/recording.md)).

::: dandy.application.bot.bot.Bot
    options:
        members:
            - __init__
            - process
            - process_to_future
            - reset

::: dandy.application.bot.exceptions

## LLM service

The main use case: prompt in, Intel out. See [Anatomy of an LLM Call](../architecture/data_flow.md)
for where this sits in the pipeline.

::: dandy.application.llm.service.LlmService
    options:
        members:
            - messages
            - config
            - options
            - prompt_to_intel
            - prompt_to_intel_future
            - append_system_prompt
            - reset
            - reset_messages

::: dandy.application.llm.mixin.LlmServiceMixin

## Tool service

The [execute-and-loop](../user_guide/tool_calling.md) use case: keeps calling the model,
running requested tools, and feeding results back until a final answer arrives.

::: dandy.application.tool.service.ToolService
    options:
        members:
            - prompt_to_intel
            - reset

::: dandy.application.tool.mixin.ToolServiceMixin

## Skill service

The [skill](../user_guide/skill.md) registry on the LLM service: holds the bot's skills,
exposes the active ones' methods as tools, and offers `activate_skill` while any
passive skill is unactivated. Access via `bot.llm.skills`.

::: dandy.application.skill.service.SkillService
    options:
        members:
            - register
            - system_prompt_section
            - active_tools
            - all_tool_names
            - activate
            - reset

::: dandy.application.skill.mixin.SkillServiceMixin

::: dandy.application.skill.tools.SkillMethodTool

::: dandy.application.skill.tools.ActivateSkillTool

## Decision

The "pick one of these" use case, documented in [Decision](../user_guide/decision.md).

::: dandy.application.decision.service.DecisionService
    options:
        members:
            - prompt_to_value
            - prompt_to_values
            - prompt_to_value_future
            - prompt_to_values_future
            - reset

::: dandy.application.decision.decision.Decision
    options:
        members:
            - __init__
            - as_enum
            - process

::: dandy.application.decision.mixin.DecisionServiceMixin

## Diligence

Post-processing passes that can be activated on a service to transform or re-check the
model's output (see the [Bots](../user_guide/bots.md) page).

::: dandy.application.diligence.diligence.BaseDiligence
    options:
        members:
            - activate
            - deactivate
            - apply

::: dandy.application.diligence.handler.DiligenceHandler
    options:
        members:
            - is_activated
            - apply
            - get_diligence
            - requires_new_llm_request

::: dandy.application.diligence.service.DiligenceService

::: dandy.application.diligence.second_pass.diligence.SecondPassRemovalDiligence

::: dandy.application.diligence.stop_word_removal.diligence.StopWordRemovalDiligence

::: dandy.application.diligence.vowel_removal.diligence.VowelRemovalDiligence

## Agent

The stateful, loop-ready base class for agentic use cases: one `turn` per exchange
over a persistent history, a `run` that drives turns until the request is
complete, and `save_session` / `load_session` for persisting the conversation.
Documented in [Agent](../user_guide/agent.md).

::: dandy.application.agent.agent.Agent
    options:
        members:
            - turn
            - run
            - clear
            - save_session
            - load_session

::: dandy.application.agent.intel.AgentTurnIntel

::: dandy.application.agent.intel.AgentSession

::: dandy.application.agent.intel.SessionRecord

::: dandy.application.agent.session_store.SessionStore
    options:
        members:
            - for_project
            - save
            - load
            - delete
            - latest
            - list_sessions
            - new_name

::: dandy.application.agent.exceptions.AgentCriticalError

::: dandy.application.agent.exceptions.AgentRecoverableError

## The coding agent

The framework's own agentic use case: a child of `Agent` that adds a planning bot
whose plan is folded into each turn's prompt, over a persistent history with
tools and context-window compaction. The CLI is a thin interface on top of it; see
[The Coding Agent](../user_guide/coding_agent.md).

::: dandy.application.agent.coding_agent.CodingAgent
    options:
        members:
            - clear

::: dandy.application.agent.session.DandyCliSession

::: dandy.application.agent.bots.coding_bot.CodingBot

::: dandy.application.agent.bots.planning_bot.PlanningBot

# Application Layer

The application layer orchestrates: it composes domain objects with infrastructure to
execute use cases. `Bot` is the entry point; the LLM, tool, decoder, and diligence
services are the use-case services that hang off it; the coding agent is the framework's
own in-house use case (the CLI's brain).

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
            - reset
            - reset_messages

::: dandy.application.llm.mixin.LlmServiceMixin

## Tool service

The [execute-and-loop](../user_guide/tool_calling.md) use case: keeps calling the model,
running requested tools, and feeding results back until a final answer arrives.

::: dandy.application.llm.tool.service.LlmToolService
    options:
        members:
            - prompt_to_intel
            - reset

::: dandy.application.llm.tool.mixin.LlmToolServiceMixin

## Decoder

The "pick one of these" use case, documented in [Decoders](../user_guide/decoders.md).

::: dandy.application.llm.decoder.service.DecoderService
    options:
        members:
            - prompt_to_value
            - prompt_to_values
            - prompt_to_value_future
            - prompt_to_values_future
            - reset

::: dandy.application.llm.decoder.decoder.Decoder
    options:
        members:
            - __init__
            - as_enum
            - process

::: dandy.application.llm.decoder.mixin.DecoderServiceMixin

## Diligence

Post-processing passes that can be activated on a service to transform or re-check the
model's output (see the [Bots](../user_guide/bots.md) page).

::: dandy.application.llm.diligence.diligence.BaseDiligence
    options:
        members:
            - activate
            - deactivate
            - apply

::: dandy.application.llm.diligence.handler.DiligenceHandler
    options:
        members:
            - is_activated
            - apply
            - get_diligence
            - requires_new_llm_request

::: dandy.application.llm.diligence.service.DiligenceService

::: dandy.application.llm.diligence.second_pass.diligence.SecondPassRemovalDiligence

::: dandy.application.llm.diligence.stop_word_removal.diligence.StopWordRemovalDiligence

::: dandy.application.llm.diligence.vowel_removal.diligence.VowelRemovalDiligence

## The coding agent

The framework's own agentic use case: a planning bot plus a coding bot over a persistent
history, with tools, planning, and context-window compaction. The CLI is a thin
interface on top of it; see [The Coding Agent](../user_guide/coding_agent.md).

::: dandy.application.agent.coding_agent.CodingAgent
    options:
        members:
            - chat
            - clear

::: dandy.application.agent.session.DandyCliSession

::: dandy.application.agent.bots.coding_bot.CodingBot

::: dandy.application.agent.bots.planning_bot.PlanningBot

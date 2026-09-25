# Domain Layer

The domain is the heart of the framework: the language of structured LLM interaction.
It contains the entities and value objects (Intel, Prompt, Message, the LLM request
body, tool descriptors) and the rules that govern them (schema generation, validation
errors, context-window compaction). It knows nothing about HTTP, files, or which LLM
endpoint it will be pointed at — those are the infrastructure's business.

The domain may depend on the [shared kernel](shared.md) and on itself, on nothing else.

## Intel

[Intel](../domain_model/glossary.md#glossary) is the value object at the center of
everything: a pydantic model describing what the LLM must return.

::: dandy.domain.intel.intel.BaseIntel
    options:
        members:
            - model_inc_ex_class_copy
            - model_to_kwargs
            - model_json_inc_ex_schema
            - model_validate_and_copy
            - model_validate_json_and_copy
            - create_from_file
            - save_to_file

::: dandy.domain.intel.intel.BaseListIntel

::: dandy.domain.intel.intel.DefaultIntel

::: dandy.domain.intel.factory.IntelFactory
    options:
        members:
            - intel_to_json_inc_ex_schema
            - json_str_to_intel_object
            - callable_signature_to_intel_class
            - simple_json_schema_to_intel_class
            - typed_kwargs_to_intel_class

::: dandy.domain.intel.service.IntelService

::: dandy.domain.intel.exceptions

## Tools

[Tools](../domain_model/glossary.md#glossary) are the domain's description of a callable
capability: a name, a description, and a `handle` whose annotated signature becomes the
OpenAI function schema. The `dandy/llm/tool/` application service is one consumer; tools
are framework-agnostic.

::: dandy.domain.tool.tool.BaseTool
    options:
        members:
            - name
            - description
            - working_directory
            - timeout_seconds
            - use_shell
            - handle
            - action_sentence
            - to_function_dict
            - get_parameters_intel_class
            - run_subprocess

::: dandy.domain.tool.tool
    options:
        members:
            - run_subprocess
            - to_tool_instances

::: dandy.domain.tool.exceptions.ToolCriticalError

## Prompts

[Prompts](../domain_model/glossary.md#glossary) are built by appending snippets and
rendering with `to_str()`. All builder methods return `self` for chaining.

::: dandy.domain.llm.prompt.prompt.Prompt
    options:
        members:
            - text
            - heading
            - sub_heading
            - title
            - list
            - unordered_list
            - ordered_list
            - array
            - array_random_order
            - unordered_random_list
            - dict
            - divider
            - line_break
            - file
            - directory_list
            - intel
            - intel_schema
            - module_source
            - object_source
            - prompt
            - random_choice
            - to_str
            - estimated_token_count

## Messages and requests

[Messages](../domain_model/glossary.md#glossary) are the wire-neutral conversation
objects. `MessageHistory` accumulates them between calls; `compact_message_history`
trims it to fit a context window (see [Options and Context](../user_guide/options_and_context.md)).

::: dandy.domain.llm.request.message.Message
    options:
        members:
            - text_content
            - estimated_token_count
            - model_dump
            - add_content_from_text
            - add_content_from_image_url
            - add_content_from_image_file_path
            - add_content_from_image_base64_string
            - add_content_from_input_audio_url
            - add_content_from_input_audio_file_path
            - add_content_from_input_audio_base64_string

::: dandy.domain.llm.request.message.MessageHistory
    options:
        members:
            - estimated_token_count
            - has_system_message
            - add_message
            - append
            - extend
            - prepend

::: dandy.domain.llm.request.message
    options:
        members:
            - compact_message_history

::: dandy.domain.llm.request.request.LlmRequestBody

## Options

[LlmOptions](../user_guide/options_and_context.md) are the tunable knobs for a request
(temperature, penalties, retry count). `max_completion_tokens` is not an option: it is
derived from the config's `CONTEXT_SIZE`.

::: dandy.domain.llm.options.LlmOptions

## Token estimation

Dependency-free token counting (character-class heuristic plus per-message framing
costs), used for context-window compaction and for prompt size estimates.

::: dandy.domain.llm.tokens.utils
    options:
        members:
            - get_estimated_token_count_for_string
            - get_estimated_token_count_for_image
            - get_estimated_token_count_for_audio
            - get_estimated_token_count_for_tool_calls

## Tool-calling and decoder values

The value objects the tool loop and the decoder produce.

::: dandy.domain.llm.tool.intel

::: dandy.domain.llm.decoder.intel

::: dandy.domain.llm.decoder.exceptions

## Exceptions

::: dandy.domain.llm.exceptions

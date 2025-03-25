from dandy.llm import LlmBot, LlmConfigOptions


class JsonSchemaLlmBot(LlmBot):
    config_options = LlmConfigOptions(
        temperature=0.0,
        prompt_retry_count=0,
    )

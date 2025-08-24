from dandy.bot import Bot
from dandy.llm.config import LlmConfigOptions


class JsonSchemaLlmBot(Bot):
    llm_config_options = LlmConfigOptions(
        temperature=0.0,
        prompt_retry_count=0,
    )

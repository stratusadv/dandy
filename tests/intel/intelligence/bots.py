from dandy.processor.bot.bot import Bot
from dandy.llm.config.options import LlmConfigOptions


class JsonSchemaBot(Bot):
    llm_config_options = LlmConfigOptions(
        temperature=0.0,
    )

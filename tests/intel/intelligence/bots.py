from dandy.processor.bot.bot import Bot
from dandy.llm.options.options import LlmOptions


class JsonSchemaBot(Bot):
    llm_options = LlmOptions(
        temperature=0.0,
    )

from dandy.bot.bot import Bot
from dandy.llm.options import LlmOptions


class JsonSchemaBot(Bot):
    llm_options = LlmOptions(
        temperature=0.0,
    )

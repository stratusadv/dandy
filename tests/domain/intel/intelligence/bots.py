from dandy.application.bot.bot import Bot
from dandy.domain.llm.options import LlmOptions


class JsonSchemaBot(Bot):
    llm_options = LlmOptions(
        temperature=0.0,
    )

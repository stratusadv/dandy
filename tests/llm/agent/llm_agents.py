from dandy.llm.bot.llm_bot import LlmBot
from dandy.llm.agent.llm_agent import BaseLlmAgent
from dandy.llm.prompt.prompt import Prompt
from tests.llm.agent.intel import EmailIntel

from tests.llm.agent.llm_bots import MuseumEmailFinderBot


class MuseumEmailLlmAgent(BaseLlmAgent[EmailIntel]):
    instructions_prompt = (
        Prompt()
        .text('Write an email to a museum based on the users input, the users email will always be the from address.')
        .text('Make up an email address to send to based on the museum name.')
    )
    intel_class = EmailIntel
    processors = (
        LlmBot,
        MuseumEmailFinderBot,
    )

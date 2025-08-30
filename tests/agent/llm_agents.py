from dandy.processor.agent.agent import Agent
from dandy.processor.bot.bot import Bot
from dandy.llm.prompt.prompt import Prompt
from tests.agent.intel import EmailIntel

from tests.agent.llm_bots import MuseumEmailFinderBot
from tests.agent.llm_maps import MuseumSubjectLlmMap
from tests.agent.workflows import EmailProofReadingBot


class MuseumEmailLlmAgent(Agent):
    instructions_prompt = (
        Prompt()
        .text('Write an email to a museum based on the users input, the users email will always be the from address.')
        .text('Figure out what subject the user would be most interested and make sure to note that in the email.')
        .text('Confirm the body of the email is well written.')
        .text('Make up an email address to send to based on the museum name.')
    )
    intel_class = EmailIntel
    processors = (
        Bot,
        MuseumEmailFinderBot,
        MuseumSubjectLlmMap,
        EmailProofReadingBot,
    )

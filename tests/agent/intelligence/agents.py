from dandy.processor.agent.agent import Agent
from dandy.processor.bot.bot import Bot
from dandy.llm.prompt.prompt import Prompt
from tests.agent.intelligence.intel import EmailIntel

from tests.agent.intelligence.bots import MuseumEmailFinderBot, EmailProofReadingBot
from tests.agent.intelligence.decoders import MuseumSubjectDecoder


class MuseumEmailAgent(Agent):
    llm_role = (
        Prompt()
        .text('Write an email to a museum based on the users request, the users provided email address will always be the from address for the final email.')
        .text('Figure out what subject the user would be most interested and make sure to note that in the email.')
        .text('Confirm the body of the email is well written.')
        .text('Make up an email address to send to based on the museum name.')
    )
    llm_intel_class = EmailIntel
    processors = (
        Bot,
        MuseumEmailFinderBot,
        MuseumSubjectDecoder,
        EmailProofReadingBot,
    )

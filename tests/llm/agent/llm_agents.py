from dandy.llm.bot.llm_bot import LlmBot
from dandy.llm.agent.llm_agent import BaseLlmAgent
from dandy.llm.prompt.prompt import Prompt
from tests.llm.agent.intel import EmailIntel

from tests.llm.agent.llm_bots import MuseumEmailFinderBot
from tests.llm.agent.llm_maps import MuseumSubjectLlmMap
from tests.llm.agent.workflows import EmailProofReadingWorkflow


class MuseumEmailLlmAgent(BaseLlmAgent[EmailIntel]):
    instructions_prompt = (
        Prompt()
        .text('Write an email to a museum based on the users input, the users email will always be the from address.')
        .text('Figure out what subject the user would be most interested and make sure to note that in the email.')
        .text('Confirm the body of the email is well written.')
        .text('Make up an email address to send to based on the museum name.')
    )
    intel_class = EmailIntel
    processors = (
        LlmBot,
        MuseumEmailFinderBot,
        MuseumSubjectLlmMap,
        EmailProofReadingWorkflow,
    )

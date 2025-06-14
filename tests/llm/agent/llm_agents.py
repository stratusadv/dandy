from dandy.llm import BaseLlmAgent, Prompt
from tests.llm.agent.intel import EmailIntel


class MuseumEmailLlmAgent(BaseLlmAgent[EmailIntel]):
    instructions_prompt = (
        Prompt()
        .text('Write an email to a museum based on the users input, the users email will always be the from address.')
        .text('Make up an email address to send to based on the museum name.')
    )
    intel_class = EmailIntel


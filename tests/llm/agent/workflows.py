from dandy.workflow.workflow import BaseWorkflow
from dandy.llm.bot.llm_bot import LlmBot
from tests.llm.agent.intel import EmailBodyIntel


class EmailProofReadingWorkflow(BaseWorkflow):
    description = 'Reads over the email body and makes sure it is a concise and informative as possible.'
    @classmethod
    def process(cls, email_body_intel: EmailBodyIntel, read_over_count: int = 2) -> EmailBodyIntel:
        for _ in range(read_over_count):
            email_body_intel = LlmBot.process(
                prompt=email_body_intel.body,
                intel_class=EmailBodyIntel,
                postfix_system_prompt='Update the user provided email body and make sure the email is a informative as possible and add some creative flair.'
            )

        return email_body_intel
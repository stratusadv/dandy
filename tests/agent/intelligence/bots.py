from dandy import Bot
from dandy.processor.bot.bot import Bot
from dandy.intel.intel import BaseIntel
from tests.agent.intelligence.intel import EmailAddressIntel, EmailBodyIntel


class MuseumEmailFinderBot(Bot):
    description = 'Finds the email address for a museum.'

    @classmethod
    def process(cls, museum_name: str) -> EmailAddressIntel:
        museum_words = museum_name.lower().split(" ")

        if 'tyrrell' in museum_words:
            return EmailAddressIntel(
                email_address='info@theroyaltyrrellmuseum.com'
            )
        else:
            return EmailAddressIntel(
                email_address=f'info@{"_".join(museum_name.lower().split(" "))}.com'
            )


class EmailProofReadingBot(Bot):
    description = 'Reads over the email body and makes sure it is a concise and informative as possible.'
    @classmethod
    def process(cls, email_body_intel: EmailBodyIntel, read_over_count: int = 2) -> EmailBodyIntel:
        for _ in range(read_over_count):
            email_body_intel = Bot().llm.prompt_to_intel(
                prompt=email_body_intel.body,
                intel_class=EmailBodyIntel,
                postfix_system_prompt='Update the user provided email body and make sure the email is a informative as possible and add some creative flair.'
            )

        return email_body_intel

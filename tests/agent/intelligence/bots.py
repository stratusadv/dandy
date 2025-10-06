from dandy import Bot
from dandy.processor.bot.bot import Bot
from dandy.intel.intel import BaseIntel
from tests.agent.intelligence.intel import EmailAddressIntel, EmailBodyIntel


class MuseumEmailFinderBot(Bot):
    description = 'Finds the email address for a museum.'

    def process(self, museum_name: str) -> EmailAddressIntel:
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

    def process(self, email_body_intel: EmailBodyIntel, read_over_count: int = 2) -> EmailBodyIntel:
        for _ in range(read_over_count):
            email_body_intel = self.llm.prompt_to_intel(
                prompt=email_body_intel.body,
                intel_class=EmailBodyIntel,
                postfix_system_prompt='Update the user provided email body and make sure the email is a informative as possible and add some creative flair.'
            )

        return email_body_intel

class EmailBodyWriterBot(Bot):
    description = 'Writes the email body based on the user provided email address.'

    def process(self, email_address_intel: EmailAddressIntel, email_body_intel: EmailBodyIntel) -> EmailBodyIntel:
        return self.llm.prompt_to_intel(
            prompt=f'Write an email to {email_address_intel.email_address} based on the users request, the users provided email address will always be the from address for the final email. Figure out what subject the user would be most interested and make sure to note that in the email. Confirm the body of the email is well written.',
            intel_class=EmailBodyIntel,
            postfix_system_prompt='Write the email body and make sure the email is a informative as possible and add some creative flair.'
        )
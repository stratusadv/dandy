from dandy.processor.bot.bot import Bot
from dandy.intel.intel import BaseIntel
from tests.agent.intel import EmailAddressIntel

class DefaultLlmIntel(BaseIntel):
    text: str

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
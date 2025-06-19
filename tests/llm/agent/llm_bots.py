from typing import Any

from dandy.bot.bot import BaseBot
from dandy.llm import DefaultLlmIntel
from tests.llm.agent.intel import EmailAddressIntel


class MuseumEmailFinderBot(BaseBot):
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
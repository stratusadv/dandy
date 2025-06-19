from typing import Any

from dandy.bot.bot import BaseBot


class MuseumEmailFinderBot(BaseBot):
    @classmethod
    def process(cls, museum_name: str) -> str:
        return f'info@{"_".join(museum_name.split(" "))}.com'
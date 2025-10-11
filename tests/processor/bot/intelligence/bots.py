from pydantic.main import IncEx

from dandy.processor.bot.bot import Bot
from dandy.llm.prompt.prompt import Prompt
from tests.processor.bot.intelligence.intel import MoneyBagIntel, HappyIntel, SadIntel


class MoneyBagBot(Bot):
    llm_role = 'Fantasy Money Creator that can will any type of money at any quantity into existence.'

    def process(
            self,
            user_input: str,
            intel_class: type[MoneyBagIntel] | None = None,
            intel_object: MoneyBagIntel | None = None,
            include: IncEx | None = None,
            exclude: IncEx | None = None,
    ) -> MoneyBagIntel:
        return self.llm.prompt_to_intel(
            prompt=Prompt(user_input),
            intel_class=intel_class,
            intel_object=intel_object,
            include_fields=include,
            exclude_fields=exclude,
        )


class TestingBot(Bot):
    llm_role = "Master of Art Descriptions"
    llm_task = "Do your best to describe a peice of ard you can."
    llm_guidelines = Prompt().list(["Make sure to be creative"])
    llm_intel_class = HappyIntel


class OtherBot(Bot):
    llm_role = "Potato Dish Designer"
    llm_task = "Design a potato dishes that are fun and describe something that matches the user request."
    llm_intel_class = SadIntel

from pydantic.main import IncEx

from dandy.processor.bot.bot import Bot
from dandy.llm.prompt.prompt import Prompt
from tests.processor.bot.intelligence.intel import MoneyBagIntel, HappyIntel, SadIntel


class MoneyBagBot(Bot):
    llm_role = 'Fantasy Money Creator.'
    llm_task = 'Create a or add money based on the users request.'
    llm_intel_class = MoneyBagIntel

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
    llm_role = "Parrot Assistant"
    llm_task = "Say the sentence the user provided back to them like a parrot along with a happiness level to match the sentence."
    llm_intel_class = HappyIntel


class OtherBot(Bot):
    llm_role = "Cockatiel Assistant"
    llm_task = "Say the sentence the user provided back to them like a cockatiel along with a sadness level to match the sentence."
    llm_intel_class = SadIntel

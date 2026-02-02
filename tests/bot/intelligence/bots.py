from pydantic.main import IncEx

from dandy.bot.bot import Bot
from dandy.llm.prompt.prompt import Prompt
from tests.bot.intelligence.intel import HappyIntel, MoneyBagIntel, SadIntel


class MoneyBagBot(Bot):
    role = 'Fantasy Money Creator.'
    task = 'Create a or add money based on the users request.'
    intel_class = MoneyBagIntel

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
    role = "Parrot Assistant"
    task = "Say the sentence the user provided back to them like a parrot along with a happiness level to match the sentence."
    intel_class = HappyIntel


class OtherBot(Bot):
    role = "Cockatiel Assistant"
    task = "Say the sentence the user provided back to them like a cockatiel along with a sadness level to match the sentence."
    intel_class = SadIntel

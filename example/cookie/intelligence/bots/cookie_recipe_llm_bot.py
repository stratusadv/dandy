from typing_extensions import List

from dandy.intel import Intel
from dandy.bot import LlmBot
from dandy.llm import Prompt
from dandy.llm.conf import llm_configs


class CookieRecipeIngredientIntel(Intel):
    name: str
    unit_type: str
    quantity: float


class CookieRecipeIntel(Intel):
    name: str
    description: str
    ingredients: List[CookieRecipeIngredientIntel]
    instructions: str


class CookieRecipeLlmBot(LlmBot):
    # If you do not set a config, the "DEFAULT" config from your "dandy_settings.py" will be used

    config = llm_configs.LLAMA_3_1_8B

    # You can also override settings per bot.

    seed = 25
    max_output_tokens = 1000

    # This is the instructions used by the system message when the llm is prompted

    instructions_prompt = (
        Prompt()
        .title('You are a cookie recipe bot.')
        .text('Your job is to follow the instructions provided below.')
        .unordered_random_list([
            'Create a cookie based on the users input',
            'Make sure the instructions are easy to follow',
            'Names of recipe should be as short as possible',
        ])
    )

    # the process function is required for all dandy handlers (bots and workflows) for debug and exception handling

    @classmethod
    def process(cls, prompt: Prompt) -> CookieRecipeIntel:
        return cls.process_prompt_to_intel(
            prompt=prompt,
            intel_class=CookieRecipeIntel,
        )
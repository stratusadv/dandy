# Exception Handling

The base to all exceptions in dandy is `DandyException` which is a subclass of `Exception` and can be used safely to handle errors within dandy.

## Probabilistic Outcomes

Working with artificial intelligence is a very different experience than conventional programming as it's more probabilistic, meaning the outcomes are less in your control.

As you develop with dandy you should consider that your code is interacting with systems you cannot be made completely deterministic.
Using exceptions to handle this will give you back the deterministic control you need to build reliable software.

## Example

```py title="main.py"
from dandy.core.exceptions import DandyException
from dandy.llm import Prompt

from example.cookie.intelligence.bots.cookie_recipe_llm_bot import CookieRecipeLlmBot


if __name__ == '__main__':
    try:
        cookie_recipe_intel = CookieRecipeLlmBot.process(
            prompt=Prompt().text('I love broccoli and oatmeal!'),
        )

        print(cookie_recipe_intel.model_dump_json(indent=4))

    except DandyException:
        print('Failed to generate a cookie recipe ... please try again')

```
# Handling Errors

We divide between `Critical` and `Recoverable` exceptions, this is to allow developers to make more decisions when it comes to handling errors.

The two primary exceptions that all other exceptions in Dandy inherit from are `DandyCriticalException` and `DandyRecoverableException`.

!!! note

    Both of these exceptions inherit from the `DandyException` which is a subclass of pythons `Exception`.



## Probabilistic Outcomes

Working with artificial intelligence is a very different experience than conventional programming as it's more probabilistic, meaning the outcomes are less in your control.
This is why we have `Critical` and `Recoverable` exceptions to make sure you can properly handle all the exceptions that can occur.

!!! tip

    As you develop with Dandy you should consider that your code is interacting with systems you cannot be made completely deterministic.
    Using exceptions to handle this will give you back the deterministic control you need to build reliable software.

## Example

Please note the following example is a simple demonstration and we would expect your exception handling code as a developer to be more robust.

```py title="main.py"
from dandy.core.exceptions import DandyException, DandyCriticalException, DandyRecoverableException
from dandy.llm import Prompt

from cookie.intelligence.bots.cookie_recipe_llm_bot import CookieRecipeLlmBot

if __name__ == '__main__':
    cookie_recipe_intel = None

    try:
        cookie_recipe_intel = CookieRecipeLlmBot.process(
            prompt=Prompt().text('I love broccoli and oatmeal!'),
        )

    except DandyRecoverableException as e:
        cookie_recipe_intel = CookieRecipeLlmBot.process(
            prompt=(
                Prompt()
                .text('I love broccoli and oatmeal!')
                .line_break()
                .text('Last time I requested a cookie recipe I got the following error:')
                .text(str(e), triple_quote=True)
            ),
        )

    except DandyCriticalException as e:
        # Please note this is just an example and not recommended practice
        raise e 

    except DandyException:
        print('Failed to generate a cookie recipe ... please try again')

    if cookie_recipe_intel:
        print(cookie_recipe_intel.model_dump_json(indent=4))
```
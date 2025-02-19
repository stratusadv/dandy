# Cookie Recipe

This example shows how to create a cookie recipe llm bot using dandy.

## Intel

We need to create some intel for our bot to use to properly structure the recipe.

```py title="cookie/intelligence/intel/cookie_intel.py"
--8<-- "example/cookie/intelligence/intel/cookie_recipe_intel.py"
```

## Bot

The cookie recipe bot is built on the `BaseLlmBot` class and uses class methods as we expect this bot to always be the same.

```py title="cookie/intelligence/bots/cookie_recipe_llm_bot.py"
--8<-- "example/cookie/intelligence/bots/cookie_recipe_llm_bot.py"
```

## Main

Simply import your cookie recipe bot and feed the `process` function a `Prompt` object.

```py title="main.py"
from dandy.llm import Prompt

from cookie.intelligence.bots.cookie_recipe_llm_bot import CookieRecipeLlmBot

cookie_recipe_intel = CookieRecipeLlmBot.process(
    prompt=Prompt().text('I love broccoli and oatmeal!'),
)

print(cookie_recipe_intel.model_dump_json(indent=4))
```

## Output

After the bot process the llm response you will be given back a cookie recipe intel object. 

```json
{
  "name": "Broccoli Oatmeal Cookies",
  "description": "A delicious cookie recipe featuring the flavors of broccoli and oatmeal.",
  "ingredients": [
    {
      "name": "All-purpose flour",
      "unit_type": "cups",
      "quantity": 2.5
    },
    {
      "name": "Rolled oats",
      "unit_type": "cups",
      "quantity": 1.0
    },
    {
      "name": "Brown sugar",
      "unit_type": "cups",
      "quantity": 0.5
    },
    {
      "name": "Granulated sugar",
      "unit_type": "cups",
      "quantity": 0.25
    },
    {
      "name": "Large eggs",
      "unit_type": "pieces",
      "quantity": 1.0
    },
    {
      "name": "Melted butter",
      "unit_type": "tablespoons",
      "quantity": 1.0
    },
    {
      "name": "Steamed broccoli florets",
      "unit_type": "cups",
      "quantity": 0.5
    },
    {
      "name": "Vanilla extract",
      "unit_type": "teaspoons",
      "quantity": 1.0
    }
  ],
  "instructions": "Preheat oven to 375°F (190°C). Line a baking sheet with parchment paper. In a medium bowl, whisk together flour, oats, brown sugar, and granulated sugar. In a large bowl, whisk together eggs, melted butter, steamed broccoli florets, and vanilla extract. Add the dry ingredients to the wet ingredients and stir until combined. Scoop tablespoon-sized balls of dough onto the prepared baking sheet, leaving 2 inches of space between each cookie. Bake for 10-12 minutes or until lightly golden brown."
}
```
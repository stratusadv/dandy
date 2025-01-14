<p align="center">
  <img src="./docs/images/dandy_logo_512.png" alt="Dandy AI Framework">
</p>


Dandy is an intelligence framework for developing programmatic intelligent bots and workflows. 
It's opinionated, simple and designed to be incredibly pythonic putting the project and developers first.

### Why Did We Create Another AI Framework?

Artificial intelligence programming is a very different experience than conventional programming as it's very probabilistic.
Based on our experience most of the existing frameworks / libraries are designed to focus more on deterministic outcomes which is not realistic or in our opinion beneficial. 

We created Dandy to focus on the flow and validation of data with your artificial intelligence systems to allow you to embrace the probabilistic nature of artificial intelligence.
Our approach is to focus on batteries included with strong tooling to help build great interactions and lowers the barrier to entry for developers.

### Pydantic is Everyones Friend

We have a class called "Intel" that is the pydantic "BaseModel" class renamed to give more separation of concerns between dandy code and your code.

This project critically relies on the use of pydantic to handle the flow and validation of data with your artificial intelligence systems. 
Make sure you have a good foundation on the use of pydantic before continuing.

Please visit https://docs.pydantic.dev/latest/ for more information on pydantic and how to utilize it.

For bigger examples please check out the [example](https://github.com/stratusadv/dandy/tree/main/example) directory in this repository.

### Installation

``` bash
pip install dandy
```

### Recommended Project Structure

```
cookie_recipe/ <-- This would be for each of your modules
    __init__.py
    your_code.py
    ...
    ...
    intelligence/ <-- Dandy related code should be in this directory
        __init__.py
        bots/
            __init__.py
            cookie_recipe_llm_bot.py <-- Should contain one bot alone (can include, intels and prompts specific to this bot)
            cookie_recipe_safety_llm_bot.py
            cookie_recipe_review_llm_bot.py
            ...
            ...
        intel/
            __init__.py
            cookie_recipe_intel.py <-- Intel Classes in all of these files must be postfixed with "Intel" ex: "SelectIntel"
            cookie_recipe_story_intel.py
            cookie_recipe_marketing_intel.py
            ...
            ...
        prompts/
            __init__.py
            cookie_recipe_prompts.py <-- All of these files would contain prompts that would be shared across the project
            cookie_recipe_email_prompts.py
            cookie_recipe_instructions_prompts.py
            ...
            ...     
        workflows/
            __init__.py
            cookie_recipe_generation_workflow.py <-- In most cases this workflow would be used to interact with the user
            ...
            ...

dandy_settings.py <-- Contains Settings, LLM configs for the entire project
```

### Setting Up Dandy

It's recommended that you have a "DANDY_SETTINGS_MODULE" in your environment variables pointed towards your dandy settings.
If no environment variable is set, it will look for "dandy_settings" module in the current working directory or sys.path.

```python
# dandy_settings.py

import os
from pathlib import Path

# This is used for controlling the debug recorder in development and should be set to false in production

ALLOW_DEBUG_RECORDING: bool = True

# You should set this to the root directory of your project the default will be the current working directory

BASE_PATH = Path.resolve(Path(__file__)).parent

# Other DEFAULT Settings - See dandy/settings.py for all options

DEFAULT_LLM_TEMPERATURE: float = 0.7
DEFAULT_LLM_SEED: int = 77
DEFAULT_LLM_RANDOMIZE_SEED: bool = False
DEFAULT_LLM_MAX_INPUT_TOKENS: int = 8000
DEFAULT_LLM_MAX_OUTPUT_TOKENS: int = 4000
DEFAULT_LLM_CONNECTION_RETRY_COUNT: int = 10
DEFAULT_LLM_PROMPT_RETRY_COUNT: int = 2

# These are some example LLM configs you may only need one of these, you must have a "DEFAULT" LLM config

LLM_CONFIGS = {
    'DEFAULT': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_HOST"),
        'PORT': int(os.getenv("OLLAMA_PORT", 11434)),
        'API_KEY': os.getenv("OLLAMA_API_KEY"),
        'MODEL': 'llama3.1:8b-instruct-q4_K_M',
    },
    'OLLAMA_LLAMA_3_2_3B_SMALL': {
        'TYPE': 'ollama',
        'HOST': os.getenv("OLLAMA_HOST"),
        'PORT': int(os.getenv("OLLAMA_PORT", 11434)),
        'API_KEY': os.getenv("OLLAMA_API_KEY"),
        'MODEL': 'llama3.2:3b-instruct-q4_K_M',
        
        # You can override any of the default settings for each LLM config
        
        'TEMPERATURE': 0.2,
        'SEED': 65,
        'RANDOMIZE_SEED': False,
        'MAX_INPUT_TOKENS': 500,
        'MAX_OUTPUT_TOKENS': 200,
    },
    'OPENAI_GPT_3_5_TURBO': {
        'TYPE': 'openai',
        'HOST': os.getenv("OPENAI_HOST"),
        'PORT': int(os.getenv("OPENAI_PORT", 443)),
        'API_KEY': os.getenv("OPEN_API_KEY"),
        'MODEL': 'gpt-3.5-turbo',
    },
}

```

### Basic Usage Example

```python
# cookie_recipe_llm_bot.py

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
    
    config = llm_configs.OPENAI_GPT_3_5_TURBO

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


    
cookie_recipe_intel = CookieRecipeLlmBot.process(
    prompt=Prompt().text('I love broccoli and oatmeal!'),
)

print(cookie_recipe_intel.model_dump_json(indent=4))
```

```json
// Output (We cannot validate the quality of this recipe, you're more then welcome to try it!)

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
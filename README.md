<p align="center">
  <img src="./docs/images/dandy_logo_512.png" alt="Dandy AI Framework">
</p>


# Dandy AI Framework
Dandy is an intelligence framework for developing programmatic intelligent bots and workflows. 
It's opinionated, simple and designed to be incredibly pythonic putting the project and developers first.

## Read First

This project critically relies on the use of pydantic to handle the flow and validation of data with your artificial intelligence models. 
Make sure you have a good foundation on the use of pydantic before continuing.

Please visit https://docs.pydantic.dev/latest/ for more information on pydantic and how to utilize it.

For bigger examples please check out the [example](https://github.com/stratusadv/dandy/tree/main/example) directory in this repository.

## Installation

``` bash
pip install dandy
```

## Project Structure

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
            cookie_recipe_llm_bot.py <-- Should contain one bot alone (can include, models and prompts specific to this bot)
            cookie_recipe_safety_llm_bot.py
            cookie_recipe_review_llm_bot.py
            ...
            ...
        intel/
            __init__.py
            cookie_recipe_intel.py <-- Pydantic Model Classes in all of these files must be postfixed with "Intel" ex: "SelectIntel"
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

## Setup

```python
# dandy_settings.py

import os
from pathlib import Path

BASE_PATH = Path.resolve(Path(__file__)).parent

# Other DEFAULT Settings - See dandy/settings.py for all options

# DEFAULT_LLM_TEMPERATURE = 0.7
# DEFAULT_LLM_SEED = 77
# DEFAULT_LLM_RANDOMIZE_SEED = False
# DEFAULT_LLM_MAX_INPUT_TOKENS = 8000
# DEFAULT_LLM_MAX_OUTPUT_TOKENS = 4000

# CONNECTION_RETRY_COUNT = 10
# PROMPT_RETRY_COUNT = 2

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

## Usage

```python
# cookie_recipe_llm_bot.py

from typing import List
from pydantic import BaseModel

from dandy.bot import LlmBot
from dandy.llm import Prompt
from dandy.llm.conf import llm_configs


class CookieRecipeIngredientIntel(BaseModel):
    name: str
    unit_type: str
    quantity: float

    
class CookieRecipeIntel(BaseModel):
    name: str
    description: str
    ingredients: List[CookieRecipeIngredientIntel]
    instructions: str

    
class CookieRecipeLlmBot(LlmBot):
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
    
    # If you do not set a config, the "DEFAULT" config will be used.
    
    config = llm_configs.OPENAI_GPT_3_5_TURBO

    # You can also override settings per bot.
    
    seed = 25

    
cookie_recipe_intel = CookieRecipeLlmBot.process(
    prompt=Prompt().text('I love broccoli and oatmeal!'),
    model=CookieRecipeIntel,
    
    # You can also override settings per prompt call.
    
    temperature=0.5,
)

print(cookie_recipe_intel.instructions)
```

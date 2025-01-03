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
        config.py <-- Contains LLM configs for this module (can be shared accross project or live elsewhere)
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
            
intelligence/ <-- Project Root where dandy related code for your entire project would live
    __init__.py
    config.py <-- Contains LLM configs for this entire project
```

## Setup

```python
# config.py

import os
from dandy.llm.config import OpenaiLlmConfig, OllamaLlmConfig

# These are some example LLM configs you may only need one of these

OPENAI_GPT_3_5_TURBO = OpenaiLlmConfig(
    host=os.getenv("OPENAI_HOST"),
    port=int(os.getenv("OPENAI_PORT", 443)),
    model='gpt-3.5-turbo',
    api_key=os.getenv("OPENAI_API_KEY"),
    max_completion_tokens=512,
)

OPENAI_GPT_4o_MINI = OpenaiLlmConfig(
    host=os.getenv("OPENAI_HOST"),
    port=int(os.getenv("OPENAI_PORT", 443)),
    model='gpt-4o-mini',
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
)

OLLAMA_LLAMA_3_2 = OllamaLlmConfig(
    host=os.getenv("OLLAMA_HOST"),
    port=int(os.getenv("OLLAMA_PORT", 11434)),
    model='llama3.2:3b-instruct',
    temperature=0.1,
)

OLLAMA_LLAMA_3_1 = OllamaLlmConfig(
    host=os.getenv("OLLAMA_HOST"),
    port=int(os.getenv("OLLAMA_PORT", 11434)),
    model='llama3.1:8b-instruct',
    max_completion_tokens=2048,
)
```

## Usage

```python
# cookie_recipe_llm_bot.py

from typing import List
from pydantic import BaseModel

from dandy.bot import LlmBot
from dandy.llm import Prompt

from cookie_recipe.intel.config import OPENAI_GPT_3_5_TURBO


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
    llm_config = OPENAI_GPT_3_5_TURBO

    
cookie_recipe_intel = CookieRecipeLlmBot.process(
    prompt=Prompt().text('I love broccoli and oatmeal!'),
    model=CookieRecipeIntel,
    temperature=0.5,
)

print(cookie_recipe_intel.instructions)
```

<p align="center">
  <img src="./docs/images/dandy_logo_512.png" alt="Dandy AI Framework">
</p>

Dandy is an intelligence framework for developing programmatic intelligent bots and workflows. It's opinionated, magical, and designed to be incredibly pythonic putting the project and developers first.

### Installation

```
pip install dandy
```

### Project Structure

```
module_a/
    your_code.py
    ...
    ...
    intelligence/ <-- Dandy Intelligence Should be in this Directory
        config.py <-- Contains LLM Configs
        agent/
            module_a_analysis_llm_agent.py
        bots/
            module_a_select_bot.py
            module_a_data_process_bot.py
            module_a_intent_llm_bot.py
            ...
            ...
        workflows/
            module_a_chat_workflow.py
            ...
            ...
```

### Modules

#### Bot

- Should accomplish one single task.

#### LLM Bots

- Should use LLMs to accomplish one single task.

#### Workflows

- Structure for combining multiple agents, bots, llm_bots, or other workflows together.

### Setup

#### Llm Config

- OpenAI & Ollama are currently supported.

```python
import os
from dandy.llm.config import OpenaiLlmConfig

OPENAI_GPT_3_5_TURBO = OpenaiLlmConfig(
    host=os.getenv("OPENAI_HOST"),
    port=int(os.getenv("OPENAI_PORT", 443)),
    model='gpt-3.5-turbo',
    api_key=os.getenv("OPENAI_API_KEY"),
)

OPENAI_GPT_4o_MINI = OpenaiLlmConfig(
    host=os.getenv("OPENAI_HOST"),
    port=int(os.getenv("OPENAI_PORT", 443)),
    model='gpt-4o-mini',
    api_key=os.getenv("OPENAI_API_KEY"),
)
```

### Usage

```python
from pydantic import BaseModel

from dandy.bot import LlmBot
from dandy.llm import Prompt

from your_module.intelligence.config import OPENAI_GPT_3_5_TURBO

class CookieRecipe(BaseModel):
    name: str
    instructions: str

class CookieRecipeLlmBot(LlmBot):
    role_prompt = Prompt().text('You are a cookie receipe bot.')
    instructions_prompt = (
      Prompt()
      .text('Your job is to follow the instructions provided below.')
      .unordered_random_list([
        'Create a cookie based on the users input',
        'Make sure the instructions are easy to follow',
        'Names of recipe should be as short as possible',
      ])
    )
    llm_config = OPENAI_GPT_3_5_TURBO

cookie_recipe = CookieRecipeLlmBot.process(
    prompt=Prompt().text('I love broccoli!'),
    model=CookieRecipe
)

print(cookie_recipe.instructions)
```

from dandy.llm.tests.configs import OPENAI_GPT_3_5_TURBO<p align="center">
  <img src="./docs/images/dandy_logo_512.png" alt="Dandy AI Framework">
</p>

## What

Dandy is a framework for developing programmatic intelligent bots and workflows. It's opinionated, magical, and designed to be incredibly pythonic.

## Why

In the pursuit of delivering incredible outcomes to our client we felt we needed a framework that could handle the demands of the future when it comes to artificial intelligence.

## Pillars of This Project

- Opinionated design with specific ways of building intelligence.
- Pythonic design that had recommended patterns and idioms.

## Getting Started

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

#### Agent

- Used to complete more complex though process with a specific output.

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
from dandy import OpenaiLlmConfig, OllamaLlmConfig

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

### Other Information


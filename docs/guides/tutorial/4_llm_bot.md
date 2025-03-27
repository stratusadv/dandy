# LLM Bot

## What is a Bot

In Dandy we want to make sure all the things you do have a distinct name to isolate them from your projects code.
Bots should represent a distinct and singular thing you want to do with in your project.

## Create You Own LLM Bot

To create your own bot we are going to use the `BaseLlmBot` class from the `dandy.llm` module.

```python exec="True" source="above" source="material-block" session="llm_bot"
from dandy.llm import BaseLlmBot

class CandyDesignBot(BaseLlmBot):
    pass

```

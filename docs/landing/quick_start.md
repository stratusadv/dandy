# Quick Start Dandy!

## Simple LLM Interaction

Once you have Dandy setup and configured you can easily get started with a simple LLM interaction.

```python exec="True" source="above" source="material-block"

from dandy.llm import LlmBot

response = LlmBot.process('What is the capital of Canada?')

print(response.text)

```

## Start Learning

Wow, that was easy ... we are only beginning to dive into the power of Dandy.

If you have already got the [setup](../guides/tutorial/1_setup.md) process complete you can skip right to the [intel tutorial](../guides/tutorial/2_intel.md).
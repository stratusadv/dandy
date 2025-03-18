# Introduction to Dandy

## Simple LLM Interaction

```python exec="True" source="above" source="material-block"

from dandy.llm import LlmBot

response = LlmBot.process('What is the capital of France?')

print(response.text)

```
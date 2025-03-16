# Introduction to Dandy

## Simple LLM Interaction

```python

from dandy.llm import LlmBot 

response = LlmBot.process('What is the capital of France?')

print(response.text)

#Output >>> Paris

```
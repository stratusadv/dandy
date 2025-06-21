# LLM Agent

## What is an Agent?

After using bots, maps and workflows, you decide that you want something that can use all of them together and will use them each at the right time.
That is where LLM Agents come in to give you an easy way to combine everything together (including other agents) in a simple-to-use package.

## Create a Basic LLM Agent

To create an agent using the `BaseLlmAgent` class from the `dandy.llm` module similar to how we created the other Dandy processors (bot, map and workflow).

```python exec="True" source="above" source="material-block" session="llm_bot"
from dandy.llm import BaseLlmAgent, LlmBot, Prompt, DefaultLlmIntel

class AssistantAgent(BaseLlmAgent):
    # This attribute is required and determines which other processors you want this agent to have access to using.
    processors = (
        LlmBot,
    )
    
intel = AssistantAgent.process('Can you give me an idea for a drawing?')

print(intel.text)
```

!!! note

    The above example only contains one processor so it will be assigned to process everything that the agent does.
    You can assign anything that is a sub class of the `BaseProcessor` which is everything in Dandy with a `process` method.
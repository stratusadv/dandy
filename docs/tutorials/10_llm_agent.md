# LLM Agent

## What is an Agent?

After using bots, maps and workflows, you decide that you want something that can use all of them together and will use them each at the right time.
That is where LLM Agents come in to give you an easy way to combine everything together (including other agents) in a simple-to-use package.

## Create a Basic LLM Agent

To create an agent using the `BaseLlmAgent` class from the `dandy.llm` module similar to how we created the other Dandy processors (bot, map and workflow).

```python exec="True" source="above" source="material-block" session="llm_agent"
from dandy.llm import BaseLlmAgent, LlmBot

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

### Example Implementation

Below is a quick demonstration on how you would build out an agent that would help you write emails to any of your favorite museums!

Setup the Required `BaseIntel` Objects.

```py title="intelligence/intel.py"
--8<-- "tests/llm/agent/intel.py"
```

Create a mock bot to help us find the museum's email address.

```py title="intelligence/bots.py"
--8<-- "tests/llm/agent/llm_bots.py"
```

Use a map to pull out the intent from the user request to discover a subject to talk about.

```py title="intelligence/maps.py"
--8<-- "tests/llm/agent/llm_maps.py"
```

Have a workflow that recursively edits the email to make it more informative and creative.

```py title="intelligence/workflows.py"
--8<-- "tests/llm/agent/workflows.py"
```

Put it all together in an Agent.

```py title="intelligence/agents.py"
--8<-- "tests/llm/agent/llm_agents.py"
```

We can now import the agent and use it to process an email.

```py title="museum.py"
from intelligence.agents import MuseumEmailLlmAgent

email_intel = MuseumEmailLlmAgent.process(
    f'The Royal Tyrell Palaeontology Museum, green colors are awesome and my email is me.person@thisplace.com'
)

print(email_intel)

```

The Agent will build a plan, user the appropriate processors and return the result as a `EmailIntel` object.

``` title="Ouput"
{
    "to_email_address": "info@theroyaltyrrellmuseum.com",
    "from_email_address": "me.person@thisplace.com",
    "subject": "Inquiry About Paleontology Exhibits and Green Colors",
    "body": "Dear Sir/Madam,\n\nI hope this message finds you well. My name is A. Person, and I am a passionate enthusiast of paleontology, particularly fascinated by the vibrant green hues found in fossilized remains. Your esteemed museum, The Royal Tyrell Palaeontology Museum, has always been a source of inspiration for my studies and curiosity.\n\nI would be immensely grateful if you could provide me with information on any upcoming exhibitions or events that focus on paleontology and the presence of green colors within fossils. Additionally, I am interested in learning more about your museum's research initiatives related to this topic.\n\nThank you very much for considering my request. I look forward to hearing from you soon.\n\nBest regards,\nA. Person"
}
```
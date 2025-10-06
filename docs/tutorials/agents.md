# Agent

## What is an Agent?

After using bots, maps and workflows, you decide that you want something that can use all of them together and will use them each at the right time.
That is where Agents come in to give you an easy way to combine everything together (including other agents) in a simple-to-use package.

## Create a Basic Agent

To create an agent using the `Agent` class from the `dandy` module similar to how we created the other Dandy processors (bot, decoder and workflow).

```python exec="True" source="above" source="material-block" session="agent"
from dandy import Agent, Bot, BaseIntel

class IdeaBot(Bot):
    llm_role = 'Creative Idea Maker'
    
    def process(self, user_input: str) -> BaseIntel:
        return self.llm.prompt_to_intel(
            prompt=user_input        
        )


class AssistantAgent(Agent):
    # This attribute is required and determines which other processors you want this agent to have access to using.
    processors = (
        IdeaBot,
    )


intel = AssistantAgent().process('Can you give me an idea for a drawing?')

print(intel.content)
```

!!! note

    The above example only contains one processor so it will be assigned to process everything that the agent does.
    You can assign anything that is a sub class of the `BaseProcessor` which is everything in Dandy with a `process` method.

### Example Implementation

Below is a quick demonstration on how you would build out an agent that would help you write emails to any of your favorite museums!

Set up the Required `BaseIntel` Objects.

```py title="intelligence/intel.py"
--8<-- "tests/agent/intelligence/intel.py"
```

Create a mock bot to help us find the museum's email address and one that recursively edits the email to make it more informative and creative.

```py title="intelligence/bots.py"
--8<-- "tests/agent/intelligence/bots.py"
```

Use a decoder to pull out the intent from the user request to discover a subject to talk about.

```py title="intelligence/decoders.py"
--8<-- "tests/agent/intelligence/decoders.py"
```

Put it all together in an Agent.

```py title="intelligence/agents.py"
--8<-- "tests/agent/intelligence/agents.py"
```

We can now import the agent and use it to process an email.

```py title="museum.py"
from intelligence.agents import MuseumEmailLlmAgent

email_intel = MuseumEmailLlmAgent().process(
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


from dandy import Agent, Bot


class AssistantAgent(Agent):
    # This attribute is required and determines which other processors you want this agent to have access to using.
    processors = (
        Bot,
    )


intel = AssistantAgent().process('Can you give me an idea for a drawing?')

print(intel.content)

# Output: Here's a creative drawing idea for you: A steampunk robot cat ...
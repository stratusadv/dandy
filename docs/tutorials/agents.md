# Agent

!!! warning "Removed in v2.0.0"

    The `Agent` module has been removed in Dandy v2.0.0. This documentation is kept for historical reference only.

    According to the v2.0.0 changelog, the Agent functionality has been removed from the framework.
    For complex workflows, consider using multiple `Bot` instances and orchestrating them manually,
    or using the `Bot` class with custom logic in your `process` method.

## What was an Agent?

In earlier versions of Dandy (v1.x), Agents provided a way to combine multiple processors (bots, decoders, and workflows) together and automatically use them at the right time.

## Migration Guide

If you were using Agents in v1.x, you can migrate to v2.0.0 by:

1. **Using Bot composition**: Create a main `Bot` class that internally uses other `Bot` instances
2. **Manual orchestration**: Explicitly call different bots in sequence based on your logic
3. **Custom process methods**: Implement your workflow logic directly in a `Bot.process()` method

### Example: Migrating from Agent to Bot

**Old approach (v1.x with Agent):**
```python
# This no longer works in v2.0.0
class AssistantAgent(Agent):
    processors = (
        IdeaBot,
        EditorBot,
    )
```

**New approach (v2.0.0 with Bot):**
```python
from dandy import Bot, BaseIntel

class IdeaBot(Bot):
    def process(self, user_input: str) -> BaseIntel:
        return self.llm.prompt_to_intel(prompt=user_input)

class EditorBot(Bot):
    def process(self, content: str) -> BaseIntel:
        return self.llm.prompt_to_intel(
            prompt=f"Edit and improve this content: {content}"
        )

class AssistantBot(Bot):
    def __post_init__(self):
        self.idea_bot = IdeaBot()
        self.editor_bot = EditorBot()

    def process(self, user_input: str) -> BaseIntel:
        # Manually orchestrate the workflow
        idea = self.idea_bot.process(user_input)
        edited = self.editor_bot.process(idea.text)
        return edited
```


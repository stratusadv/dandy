from dandy import Bot, Prompt

class AssistantBot(Bot):
    def process(self, user_prompt: Prompt | str):
        default_intel = self.llm.prompt_to_intel(
            prompt=user_prompt,
        )

        return default_intel

intel = AssistantBot().process('Can you give me an idea for a book?')

print(intel.content)

# Output: Here's an idea for a book: 'The Memory Thief's Daughter' - A mystery thriller ...
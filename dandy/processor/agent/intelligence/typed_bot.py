from dandy import Bot, BaseIntel
from dandy.llm.prompt.typing import PromptOrStr


class TypedBot(Bot):
    def process(
            self,
            prompt: PromptOrStr,
            intel_class: type[BaseIntel],
    ) -> BaseIntel:
        return self.llm.prompt_to_intel(
            prompt=prompt,
            intel_class=intel_class,
        )

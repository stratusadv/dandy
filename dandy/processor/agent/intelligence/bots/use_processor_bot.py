from typing import Type

from dandy.processor.bot.bot import Bot
from dandy.intel.intel import BaseIntel
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.prompt.typing import PromptOrStr


class UseProcessorBot(Bot):
    llm_role = 'You are a bot that is given a task and a processor, provide a response that best uses the processor to complete the task.'

    def process(
        self,
        prompt: PromptOrStr,
        processor_kwargs_intel_class: Type[BaseIntel],
        processor_description: str,
    ) -> BaseIntel:
        return self.llm.prompt_to_intel(
            prompt=(
                Prompt()
                .sub_heading('Task:')
                .prompt(prompt)
                .sub_heading('Resource:')
                .text(processor_description)
            ),
            intel_class=processor_kwargs_intel_class,
        )

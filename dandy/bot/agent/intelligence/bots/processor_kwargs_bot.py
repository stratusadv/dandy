from typing import Type

from dandy.processor.bot.bot import Bot
from dandy.intel.intel import BaseIntel
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.prompt.typing import PromptOrStr


class ProcessorKwargsBot(Bot):
    llm_role = 'Useful Response Generator'
    llm_task = 'Take the given a task and a resource, provide a response that could be best used the resource to complete the task.'

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

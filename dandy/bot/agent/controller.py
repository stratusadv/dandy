from pydantic.main import IncEx
from typing import Type

from dandy.processor.agent.exceptions import AgentCriticalException
from dandy.processor.agent.intelligence.bots.answer_transfer_bot import (
    AnswerTransferBot,
)
from dandy.processor.agent.intelligence.bots.processor_kwargs_bot import ProcessorKwargsBot
from dandy.core.typing.tools import get_typed_kwargs_from_callable_signature
from dandy.intel.generator import IntelClassGenerator

from dandy.intel.intel import BaseIntel
from dandy.llm.prompt.typing import PromptOrStr
from dandy.processor.processor import BaseProcessor


class ProcessorController:
    def __init__(self, processor_class: Type[BaseProcessor]):
        if not issubclass(processor_class, BaseProcessor):
            message = f'{processor_class} is not a sub class of "BaseProcessor"'
            raise AgentCriticalException(message)

        self.processor_class = processor_class

    def use(
        self,
        prompt: PromptOrStr,
        intel_object: BaseIntel,
        include_fields: IncEx | None = None,
        exclude_fields: IncEx | None = None,
    ) -> BaseIntel | None:
        available_kwargs_and_values = {
            'prompt': prompt,
            'intel_object': intel_object,
            'include_fields': include_fields,
            'exclude_fields': exclude_fields,
        }

        required_processor_typed_kwargs = get_typed_kwargs_from_callable_signature(
            callable_=self.processor_class().process,
            return_defaulted=False,
        )

        if required_processor_typed_kwargs in get_typed_kwargs_from_callable_signature(
            self.use
        ):
            processor_intel = self.processor_class().process(
                **{
                    key: available_kwargs_and_values[key]
                    for key in required_processor_typed_kwargs
                    if key in available_kwargs_and_values
                }
            )

            if isinstance(processor_intel, type(intel_object)):
                return processor_intel

        else:
            processor_kwargs_intel_class = IntelClassGenerator.from_typed_kwargs(
                intel_class_name=f'{self.processor_class.__qualname__}Intel',
                typed_kwargs=get_typed_kwargs_from_callable_signature(
                    callable_=self.processor_class().process,
                ),
            )

            processor_kwargs_intel = ProcessorKwargsBot().process(
                prompt=prompt,
                processor_kwargs_intel_class=processor_kwargs_intel_class,
                processor_description=self.processor_class.get_description(),
            )

            processor_intel = self.processor_class().process(
                **processor_kwargs_intel.model_to_kwargs()
            )

        if not issubclass(processor_intel.__class__, BaseIntel):
            message = (
                f'Processor {self.processor_class.__name__} did not return an instance of "BaseIntel" while being used as a resource. '
                f'It returned an instance of {processor_intel.__class__.__name__}.'
            )
            raise AgentCriticalException(message)

        return AnswerTransferBot().process(
            answer_intel=processor_intel,
            task_intel=intel_object,
            task_prompt=prompt,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
        )

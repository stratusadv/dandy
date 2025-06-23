from typing import Any

from pydantic.main import IncEx
from typing_extensions import Union, Type, Tuple, Dict

from dandy.agent.exceptions import AgentCriticalException
from dandy.core.processor.controller import BaseProcessorController
from dandy.core.typing.typing import TypedKwargsDict
from dandy.core.typing.tools import get_typed_kwargs_dict_from_callable
from dandy.intel.generator import IntelClassGenerator
from dandy.llm.bot.llm_bot import LlmBot, BaseLlmBot
from dandy.llm.prompt.prompt import Prompt

from dandy.intel.intel import BaseIntel


class UseProcessorLlmBot(BaseLlmBot):
    instructions_prompt = 'You are a bot that is given a task and a processor, provide a response that best uses the processor to complete the task.'

    @classmethod
    def process(
            cls,
            prompt: Prompt,
            processor_kwargs_intel_class: Type[BaseIntel],
            processor_description: str
    ) -> BaseIntel:
        return cls.process_prompt_to_intel(
            prompt=(
                Prompt()
                .sub_heading('Task:')
                .prompt(prompt)
                .sub_heading('Resource:')
                .text(processor_description)
            ),
            intel_class=processor_kwargs_intel_class,
        )


class LlmProcessorController(BaseProcessorController):
    def use(
            self,
            prompt: Prompt,
            intel_object: BaseIntel,
            include_fields: Union[IncEx, None] = None,
            exclude_fields: Union[IncEx, None] = None,
    ) -> BaseIntel | None:
        available_kwargs_and_values = {
            'prompt': prompt,
            'intel_object': intel_object,
            'include_fields': include_fields,
            'exclude_fields': exclude_fields,
        }

        required_processor_kwargs = get_typed_kwargs_dict_from_callable(
            callable_=self.processor.process,
            return_defaulted=False,
        )

        if self._check_if_use_kwargs_match_typed_kwargs(required_processor_kwargs):
            pass

        if self.processor is LlmBot:
            return self.processor.process(**available_kwargs_and_values)

        else:
            processor_kwargs_intel_class = IntelClassGenerator.from_attributes_dict(
                intel_class_name=f'{self.processor.__qualname__}Intel',
                attributes_dict=get_typed_kwargs_dict_from_callable(
                    callable_=self.processor.process,
                ),
            )

            processor_kwargs_intel = UseProcessorLlmBot.process(
                prompt=prompt,
                processor_kwargs_intel_class=processor_kwargs_intel_class,
                processor_description=self.processor.description
            )

            processor_intel = self.processor.process(
                **processor_kwargs_intel.model_to_kwargs()
            )

            if not issubclass(processor_intel.__class__, BaseIntel):
                raise AgentCriticalException(
                    f'Processor {self.processor.__name__} did not return an instance of "BaseIntel" while being used as a resource. It returned an instance of {processor_intel.__class__.__name__}.'
                )

            return LlmBot.process(
                prompt=(
                    Prompt()
                    .text('Fill out the actual result to this task using the answer below.')
                    .text('This answer does not need to be validated.')
                    .line_break()
                    .sub_heading('Task:')
                    .prompt(prompt)
                    .line_break()
                    .sub_heading('Answer:')
                    .intel(processor_intel)
                ),
                intel_object=intel_object,
                include_fields=include_fields,
                exclude_fields=exclude_fields,
            )

    @property
    def _use_typed_kwargs(self) -> TypedKwargsDict:
        return get_typed_kwargs_dict_from_callable(
            callable_=self.use
        )


    def _check_if_use_kwargs_match_typed_kwargs(
            self,
            typed_kwargs: TypedKwargsDict,
    ) -> bool:
        if typed_kwargs.keys() >= self._use_typed_kwargs.keys():
            pass

        return False

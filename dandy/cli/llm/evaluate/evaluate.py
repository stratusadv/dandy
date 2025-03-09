import importlib
import inspect
from enum import Enum

from typing_extensions import Union

from dandy.cli.llm.evaluate.intelligence.prompts.prompt_evaluation_prompts import evaluate_prompt_system_prompt, \
    evaluate_prompt_user_prompt
from dandy.intel import BaseIntel
from dandy.llm.service.config import BaseLlmConfig


class EvaluatedSourceIntel(BaseIntel):
    file_name: str
    source: str
    source_changed: bool
    evaluator_comments: str


class EvaluateChoices(Enum):
    PROMPT = 'prompt'


def evaluate(
        llm_config: BaseLlmConfig,
        choice: EvaluateChoices,
        module_and_obj: Union[str, None] = None,
        evaluate_description: Union[str, None] = None,
) -> None:

    if module_and_obj is None:
        module_and_obj = input('Enter the module and object you want to evaluate: ')

    if evaluate_description is None:
        evaluate_description = input('Describe the prompt you want to evaluate: ')

    print(f'Evaluating {choice.value} {module_and_obj} ... depending on your llm configuration this may take up to a couple minutes')

    module_name = ".".join(module_and_obj.split(".")[0:-1])
    obj_name = module_and_obj.split(".")[-1]

    print(f'Module: {module_name}')
    module = importlib.import_module(module_name)

    print(f'Object: {obj_name}')
    obj = getattr(module, obj_name)

    source_code = inspect.getsource(obj)

    if choice == EvaluateChoices.PROMPT:
        evaluated_source_intel = llm_config.service.process_prompt_to_intel(
            prompt=evaluate_prompt_user_prompt(
                prompt_name=obj_name,
                prompt_source=source_code,
                prompt_description=evaluate_description,
            ),
            intel_class=EvaluatedSourceIntel,
            system_prompt=evaluate_prompt_system_prompt(),
        )

        if evaluated_source_intel:
            print(f'{evaluated_source_intel.source_changed=}')
            print(evaluated_source_intel.source + '\n')
            print(evaluated_source_intel.evaluator_comments + '\n')

        else:
            print('Failed to get response from the assistant ... try again')

    else:
        raise ValueError(f'Unknown evaluate type: {choice}')
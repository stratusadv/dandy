import os

from pydantic import BaseModel
from typing import Any, Type

from dandy.bot import LlmBot
from dandy.debug.debug import DebugRecorder
from dandy.llm.config.ollama import OllamaLlmConfig
from dandy.llm.prompt import Prompt
from tests.models.tradesman_model import GroupBase


class SeedLlmBot(LlmBot):
    llm_config = OllamaLlmConfig(
        host=os.getenv('OLLAMA_HOST'),
        port=os.getenv('OLLAMA_PORT'),
        model='llama3.1',
        temperature=1.0,
    )

    role_prompt = (
        Prompt()
        .text('You are a data generation bot tasked with generating realistic data for Pydantic models.')
    )

    instructions_prompt = (
        Prompt()
        .text('Your job is to create data for seeding the database of Tradesman Manufacturing, a Canadian HVAC sheet metal product manufacturer.')
        .text('Generate realistic information for each field in the provided Pydantic model, including products, client names, and facility details.')
        .text('The data should reflect real-world manufacturing operations and is specific to HVAC systems.')
        .text('Please avoid generic names; use realistic details as if the data is from a real plant.')
    )

    @classmethod
    def process(cls, model: Type[BaseModel], **kwargs: Any) -> BaseModel:
        prompt = (
            cls.instructions_prompt
            .text('Generate the data for the following Pydantic model:')
        )

        model_instance = cls.process_prompt_to_model_object(
            prompt=prompt,
            model=model,
            **kwargs
        )

        return model_instance


def main() -> None:
    DebugRecorder.start_recording('playground')

    work_order_instance = SeedLlmBot.process(GroupBase)
    print(work_order_instance.json())

    DebugRecorder.stop_recording('playground')
    DebugRecorder.to_html('playground')


if __name__ == '__main__':
    main()

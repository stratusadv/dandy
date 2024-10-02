from typing import Type

from pydantic import BaseModel

from dandy.bot import LlmBot
from dandy.llm.prompt import Prompt


class SeedLlmBot(LlmBot):
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
    def process(cls, model: Type[BaseModel], **kwargs) -> BaseModel:
        prompt = (
            cls.instructions_prompt
            .text('Generate the data for the following Pydantic model:')
        )

        model_instance = cls.process_prompt_to_model_object(
            prompt=prompt,
            model=model,
        )

        return model_instance



from abc import ABC, abstractmethod
from typing import Type, Union

from pydantic import BaseModel

from dandy.handler.handler import BaseHandler
from dandy.llm.prompt import Prompt


class Agent(BaseHandler):
    role_prompt: Prompt
    instructions_prompt: Prompt

    @abstractmethod
    def process(
            self,
            model: Type[BaseModel],
            model_object: BaseModel,
    ) -> Union[Type[BaseModel], BaseModel]: ...
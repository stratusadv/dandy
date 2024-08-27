from typing import Type, Union

from pydantic import BaseModel

from dandy.handler.handler import BaseHandler


class Tool(BaseHandler):
    def process(
            self,
            model: Type[BaseModel],
            model_object: BaseModel,
    ) -> Union[Type[BaseModel], BaseModel]: ...
from pydantic import BaseModel
from typing_extensions import Union, List, Any, Literal

from dandy.llm.service.request.message import RequestMessage, RoleLiteralStr
from dandy.llm.service.request.request import BaseRequestBody
from dandy.llm.tokens.utils import get_estimated_token_count_for_string


class OllamaRequestOptions(BaseModel):
    num_ctx: Union[int, None] = None
    num_predict: Union[int, None] = None
    seed: Union[int, None] = None
    temperature: Union[float, None] = None


class OllamaRequestBody(BaseRequestBody):
    options: OllamaRequestOptions
    stream: bool = False
    format: Union[dict, None] = {}

    def add_message(
            self,
            role: RoleLiteralStr,
            content: str,
            images: Union[List[str], None] = None
    ) -> None:
        self.messages.append(
            RequestMessage(
                role=role,
                content=content,
                images=images
            )
        )

    def get_context_length(self) -> int:
        return self.options.num_ctx

    @property
    def token_usage(self) -> int:
        token_usage = int(sum([get_estimated_token_count_for_string(message.content) for message in self.messages]))
        token_usage += get_estimated_token_count_for_string(str(self.format))

        return token_usage

    def get_max_completion_tokens(self) -> int:
        return self.options.num_predict

    def get_seed(self):
        return self.options.seed

    def get_temperature(self):
        return self.options.temperature

    def set_format_to_json_schema(self, json_schema: dict):
        self.format = json_schema

    def set_format_to_text(self):
        self.format = None

    def to_dict(self) -> dict:
        return self.model_dump()
from typing import List

from pydantic import BaseModel

from dandy.llm.request.message import RequestMessage, RoleLiteralStr
from dandy.llm.request.request import BaseRequestBody
from dandy.llm.tokens.utils import get_estimated_token_count_for_string


class OllamaRequestMessage(RequestMessage):
    def content_as_str(self) -> str:
        return self.content


class OllamaRequestOptions(BaseModel):
    num_ctx: int | None = None
    num_predict: int | None = None
    seed: int | None = None
    temperature: float | None = None


class OllamaRequestBody(BaseRequestBody):
    options: OllamaRequestOptions
    stream: bool = False
    format: dict | None = {}

    def add_message(
        self,
        role: RoleLiteralStr,
        content: str,
        images: List[str] | None = None,
        prepend: bool = False,
    ) -> None:
        ollama_request_message = OllamaRequestMessage(role=role, content=content, images=images)

        if prepend:
            self.messages.insert(0, ollama_request_message)
        else:
            self.messages.append(ollama_request_message)

    def get_context_length(self) -> int:
        return self.options.num_ctx

    @property
    def token_usage(self) -> int:
        token_usage = int(
            sum(
                [
                    get_estimated_token_count_for_string(message.content)
                    for message in self.messages
                ]
            )
        )
        token_usage += get_estimated_token_count_for_string(str(self.format))

        return token_usage

    def get_max_completion_tokens(self) -> int | None:
        return self.options.num_predict

    def get_seed(self) -> int | None:
        return self.options.seed

    def get_temperature(self) -> float | None:
        return self.options.temperature

    def set_format_to_json_schema(self, json_schema: dict):
        self.format = json_schema

    def set_format_to_text(self):
        self.format = None

    def to_dict(self) -> dict:
        return self.model_dump()

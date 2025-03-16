from typing_extensions import Union, List

from dandy.llm.service.request.message import RequestMessage
from dandy.llm.service.request.request import BaseRequestBody
from dandy.llm.utils import get_image_mime_type_from_base64_string


class OpenaiRequestBody(BaseRequestBody):
    stream: bool = False
    # Some OpenAI Models require strict to be True ... Why ... I don't know!
    response_format: dict = { 'type': 'json_schema', 'json_schema': {'name': 'response', 'strict': False,  'schema': ...} }
    max_completion_tokens: Union[int, None] = None
    seed: Union[int, None] = None
    temperature: Union[float, None] = None

    def add_message(
            self,
            role: str,
            content: str,
            images: Union[List[str], None] = None
    ) -> None:
        message_content: List[dict] = [{
            'type': 'text',
            'text': content,
        }]

        if images is not None:
            for image in images:
                message_content.append({
                    'type': 'image_url',
                    'image_url': {
                        'url': f'data:{get_image_mime_type_from_base64_string(image)};base64,{image}'
                    }
                })

        self.messages.append(
            RequestMessage(
                role=role,
                content=message_content,
            )
        )

    def get_context_length(self) -> int:
        return 0

    def get_max_completion_tokens(self) -> int:
        return self.max_completion_tokens

    def get_seed(self) -> int:
        return self.seed

    def get_temperature(self) -> float:
        return self.temperature

    def set_format_to_json_schema(self, json_schema: dict):
        self.response_format['json_schema']['schema'] = json_schema

        # Required for some OpenAI Models ... Why ... I don't know!
        # self.response_format['json_schema']['schema']['additionalProperties'] = False

    def set_format_to_text(self):
        self.response_format = {'type': 'text'}
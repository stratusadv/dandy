from typing_extensions import Union, List, Literal

from dandy.llm.service.request.message import RequestMessage, RoleLiteralStr
from dandy.llm.service.request.request import BaseRequestBody
from dandy.llm.tokens.utils import get_estimated_token_count_for_string
from dandy.llm.utils import get_image_mime_type_from_base64_string


class OpenaiRequestBody(BaseRequestBody):
    stream: bool = False
    # Some OpenAI Models require strict to be True ... Why ... I don't know!
    response_format: dict = {'type': 'json_schema', 'json_schema': {'name': 'response', 'strict': False, 'schema': ...}}
    max_completion_tokens: Union[int, None] = None
    seed: Union[int, None] = None
    temperature: Union[float, None] = None

    def add_message(
            self,
            role: RoleLiteralStr,
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

    @property
    def token_usage(self) -> int:
        token_usage = int(sum([get_estimated_token_count_for_string(message.content) for message in self.messages]))
        token_usage += get_estimated_token_count_for_string(str(self.response_format))

        return token_usage

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

    def to_dict(self) -> dict:
        model_dict = self.model_dump()
        formated_messages = []
        for message in model_dict['messages']:
            for content in message['content']:
                if content['type'] == 'text':
                    formated_messages.append({
                        'role': message['role'],
                        'content': content['text'],
                    })
                elif content['type'] == 'image_url':
                    formated_messages.append({
                        'role': message['role'],
                        'content': content['image_url']['url'].split(';base64,')[1],
                    })

        model_dict['messages'] = formated_messages

        return model_dict

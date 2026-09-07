from pydantic import BaseModel, Field, ConfigDict

from dandy.llm.request.message import MessageHistory
from dandy.llm.tokens.utils import get_estimated_token_count_for_string


class LlmRequestBody(BaseModel):
    model: str
    messages: MessageHistory = Field(default_factory=MessageHistory)
    stream: bool = False
    tools: list[dict] | None = None
    tool_choice: str | dict | None = None

    response_format: dict | None = {
        'type': 'json_schema',
        'json_schema': {
            'name': 'response_data',
            'strict': True,
            'schema': ...
        },
    }

    model_config = ConfigDict(
        extra='allow'
    )

    @property
    def estimated_token_count(self) -> int:
        response_format_token_count = 0

        if self.response_format is not None:
            response_format_token_count = get_estimated_token_count_for_string(
                str(self.response_format['json_schema']['schema'])
            )

        return self.messages.estimated_token_count + response_format_token_count

    @property
    def json_schema(self) -> dict:
        return self.response_format['json_schema']['schema']

    @json_schema.setter
    def json_schema(self, json_schema: dict):
        if self.response_format is not None:
            self.response_format['json_schema']['schema'] = json_schema

    def model_dump(self, *args, **kwargs) -> dict:
        model_dict = super().model_dump(*args, exclude_none=True, **kwargs)
        model_dict['messages'] = [
            message.model_dump()
            for message in self.messages.messages
        ]

        return model_dict

    def reset_messages(self):
        self.messages = MessageHistory()

    def to_dict(self) -> dict:
        model_dict = self.model_dump()

        formated_messages = []

        for message in model_dict['messages']:
            for content in message['content']:
                if content['type'] == 'text':
                    formated_messages.append(
                        {
                            'role': message['role'],
                            'content': content['text'],
                        }
                    )
                elif content['type'] == 'image_url':
                    formated_messages.append(
                        {
                            'role': message['role'],
                            'content': content['image_url']['url'].split(';base64,')[1],
                        }
                    )

        model_dict['messages'] = formated_messages

        return model_dict

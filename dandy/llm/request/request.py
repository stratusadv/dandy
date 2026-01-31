from pydantic import BaseModel, Field

from dandy.llm.options import LlmOptions
from dandy.llm.request.message import MessageHistory


class LlmRequestBody(BaseModel):
    model: str
    messages: MessageHistory = Field(default_factory=MessageHistory)
    stream: bool = False

    response_format: dict = {
        'type': 'json_schema',
        'json_schema': {
            'name': 'response_data',
            'strict': True,
            'schema': ...
        },
    }

    class Config:
        extra = 'allow'

    @property
    def estimated_token_count(self) -> int:
        return self.messages.estimated_token_count

    @property
    def json_schema(self) -> dict:
        return self.response_format['json_schema']['schema']

    @json_schema.setter
    def json_schema(self, json_schema: dict):
        self.response_format['json_schema']['schema'] = json_schema

    def model_dump(self, *args, **kwargs) -> dict:
        model_dict = super().model_dump(*args, exclude_none=True, **kwargs)
        model_dict['messages'] = model_dict.pop('messages')['messages']

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

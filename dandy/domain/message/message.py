from pathlib import Path
from typing import Any, Iterator, Literal

from pydantic import BaseModel, Field, field_validator

from dandy.shared.files import encode_file_to_base64, get_file_extension_from_url_string
from dandy.shared.hashing import HashMixin, dump_model
from dandy.shared.media import (
    get_audio_format_from_base64_string,
    get_image_mime_type_from_base64_string,
)
from dandy.domain.tokens.estimate import (
    TOKEN_COUNT_REQUEST_OVERHEAD,
    TOKEN_COUNT_ROLE_OVERHEAD,
    TOKEN_COUNT_TOOL_CALL_ID_OVERHEAD,
    get_estimated_token_count_for_audio,
    get_estimated_token_count_for_image,
    get_estimated_token_count_for_string,
    get_estimated_token_count_for_tool_calls,
)

RoleLiteralStr = Literal['user', 'assistant', 'system', 'tool']
DetailLiteralStr = Literal['auto', 'low', 'high']
TypeLiteralStr = Literal['text', 'image_url', 'input_audio']


class ImageUrl(BaseModel):
    url: str
    detail: DetailLiteralStr = 'auto'


class InputAudio(BaseModel):
    data: str
    format: str

    def as_data_encoded_base64(self) -> str:
        return f'data:audio/{self.format};base64,{self.data}'


class MessageContent(BaseModel):
    type: TypeLiteralStr
    text: str | None = None
    image_url: ImageUrl | None = None
    input_audio: InputAudio | None = None

    def as_str(self) -> str:
        if self.type == 'text' and self.text:
            return self.text

        if self.type == 'image_url' and self.image_url:
            return self.image_url.__str__()

        if self.type == 'input_audio' and self.input_audio:
            return self.input_audio.as_data_encoded_base64()

        return self.__str__()


class Message(HashMixin, BaseModel):
    role: RoleLiteralStr
    content: list[MessageContent] = Field(default_factory=list)
    tool_call_id: str | None = None
    tool_calls: list[dict] | None = None

    def hash_state(self) -> Any:
        return dump_model(super().model_dump)

    @field_validator('content', mode='before')
    @classmethod
    def _coerce_wire_content(cls, value: object) -> object:
        """Accept the OpenAI wire shape, where tool content is a plain string."""
        if value is None:
            return []

        if isinstance(value, str):
            return [MessageContent(type='text', text=value)]

        return value

    @property
    def text_content(self) -> str:
        return ''.join(
            message_content.text or '' for message_content in self.content if message_content.text
        )

    @property
    def estimated_token_count(self) -> int:
        token_count = TOKEN_COUNT_ROLE_OVERHEAD

        if self.tool_call_id:
            token_count += TOKEN_COUNT_TOOL_CALL_ID_OVERHEAD + get_estimated_token_count_for_string(
                self.tool_call_id
            )

        if self.tool_calls:
            token_count += get_estimated_token_count_for_tool_calls(self.tool_calls)
        else:
            for message_content in self.content:
                if message_content.type == 'text' and message_content.text:
                    token_count += get_estimated_token_count_for_string(message_content.text)
                elif message_content.type == 'image_url' and message_content.image_url:
                    token_count += get_estimated_token_count_for_image(
                        message_content.image_url.detail
                    )
                elif message_content.type == 'input_audio' and message_content.input_audio:
                    token_count += get_estimated_token_count_for_audio(
                        message_content.input_audio.data
                    )

        return token_count

    def model_dump(self, *args, **kwargs) -> dict:
        kwargs['exclude_none'] = True
        model_dict = super().model_dump(*args, **kwargs)

        if self.role == 'tool':
            model_dict['content'] = self.text_content
        elif self.tool_calls:
            model_dict['content'] = None

        return model_dict

    def add_content_from_text(self, text: str) -> None:
        self.content.append(MessageContent(type='text', text=text))

    def add_content_from_image_url(self, image_url: str) -> None:
        self.content.append(MessageContent(type='image_url', image_url=ImageUrl(url=image_url)))

    def add_content_from_image_file_path(self, image_file_path: Path | str) -> None:
        self.add_content_from_image_base64_string(
            image_base64_string=encode_file_to_base64(image_file_path)
        )

    def add_content_from_image_base64_string(self, image_base64_string: str) -> None:
        self.content.append(
            MessageContent(
                type='image_url',
                image_url=ImageUrl(
                    url=f'data:{get_image_mime_type_from_base64_string(image_base64_string)};base64,{image_base64_string}'
                ),
            )
        )

    def add_content_from_input_audio_url(self, input_audio_url: str) -> None:
        self.content.append(
            MessageContent(
                type='input_audio',
                input_audio=InputAudio(
                    data=input_audio_url, format=get_file_extension_from_url_string(input_audio_url)
                ),
            )
        )

    def add_content_from_input_audio_file_path(self, input_audio_file_path: Path | str) -> None:
        self.add_content_from_input_audio_base64_string(
            input_audio_base64_string=encode_file_to_base64(input_audio_file_path)
        )

    def add_content_from_input_audio_base64_string(self, input_audio_base64_string: str) -> None:
        self.content.append(
            MessageContent(
                type='input_audio',
                input_audio=InputAudio(
                    data=input_audio_base64_string,
                    format=get_audio_format_from_base64_string(input_audio_base64_string),
                ),
            )
        )


class MessageHistory(HashMixin, BaseModel):
    messages: list[Message] = Field(default_factory=list)

    def __len__(self) -> int:
        return len(self.messages)

    def __getitem__(self, index: int) -> list[Message] | Message:
        return self.messages[index]

    def __iter__(self) -> Iterator[list[Message] | Message]:
        yield from self.messages

    def __setitem__(self, index: int, message: Message) -> None:
        self.messages[index] = message

    @property
    def estimated_token_count(self) -> int:
        return TOKEN_COUNT_REQUEST_OVERHEAD + sum(
            message.estimated_token_count for message in self.messages
        )

    @property
    def has_system_message(self) -> bool:
        return len(self.messages) > 0 and self.messages[0].role == 'system'

    def add_message(
        self,
        role: RoleLiteralStr,
        text: str | None = None,
        image_urls: list[str] | None = None,
        image_file_paths: list[Path | str] | None = None,
        image_base64_strings: list[str] | None = None,
        audio_urls: list[str] | None = None,
        audio_file_paths: list[str] | None = None,
        audio_base64_strings: list[str] | None = None,
        tool_call_id: str | None = None,
        tool_calls: list[dict] | None = None,
        prepend: bool = False,
    ) -> None:
        message = Message(role=role, tool_call_id=tool_call_id, tool_calls=tool_calls)

        if text is not None:
            message.add_content_from_text(text=text)

        for image_url in image_urls or []:
            message.add_content_from_image_url(image_url=image_url)

        for image_file_path in image_file_paths or []:
            message.add_content_from_image_file_path(image_file_path=image_file_path)

        for image_base64_string in image_base64_strings or []:
            message.add_content_from_image_base64_string(image_base64_string=image_base64_string)

        for audio_url in audio_urls or []:
            message.add_content_from_input_audio_url(input_audio_url=audio_url)

        for audio_file_path in audio_file_paths or []:
            message.add_content_from_input_audio_file_path(input_audio_file_path=audio_file_path)

        for audio_base64_string in audio_base64_strings or []:
            message.add_content_from_input_audio_base64_string(
                input_audio_base64_string=audio_base64_string
            )

        if prepend:
            self.prepend(message)
        else:
            self.append(message)

    def append(self, message: Message) -> None:
        self.messages.append(message)

    def extend(self, messages: list[Message]) -> None:
        self.messages.extend(messages)

    def prepend(self, message: Message) -> None:
        self.messages.insert(0, message)

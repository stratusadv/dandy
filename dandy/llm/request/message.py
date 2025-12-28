from pathlib import Path
from typing import List, Literal, Self, Iterator

from pydantic import BaseModel, Field

from dandy.llm.tokens.utils import get_estimated_token_count_for_string
from dandy.llm.utils import get_image_mime_type_from_base64_string, get_audio_format_from_base64_string, \
    get_file_extension_from_url_string

RoleLiteralStr = Literal['user', 'assistant', 'system']
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
        if self.type == 'text':
            return self.text

        elif self.type == 'image_url':
            return self.image_url.__str__()

        elif self.type == 'input_audio':
            return self.input_audio.as_data_encoded_base64()

        else:
            return self.__str__()


class Message(BaseModel):
    role: RoleLiteralStr
    content: MessageContent

    @property
    def estimated_token_count(self) -> int:
        return get_estimated_token_count_for_string(self.__str__()) + 1

    @classmethod
    def from_text(cls, role: RoleLiteralStr, text: str) -> Self:
        return cls(role=role, content=MessageContent(type='text', text=text))

    @classmethod
    def from_image_url(cls, role: RoleLiteralStr, image_url: str) -> Self:
        return cls(role=role, content=MessageContent(type='image_url', image_url=ImageUrl(url=image_url)))

    @classmethod
    def from_image_file_path(cls, role: RoleLiteralStr, image_file_path: Path | str) -> Self:
        with open(Path(image_file_path), 'rb') as image_file:
            return cls.from_image_base64_string(
                role=role,
                image_base64_string=image_file.read().decode("base64")
            )

    @classmethod
    def from_image_base64_string(cls, role: RoleLiteralStr, image_base64_string: str) -> Self:
        return cls(
            role=role,
            content=MessageContent(
                type='image_url',
                image_url=ImageUrl(
                    url=f'data:image/data:{get_image_mime_type_from_base64_string(image_base64_string)};base64,{image_base64_string}'
                )
            )
        )

    @classmethod
    def from_input_audio_url(cls, role: RoleLiteralStr, input_audio_url: str) -> Self:
        return cls(
            role=role,
            content=MessageContent(
                type='input_audio',
                input_audio=InputAudio(
                    data=input_audio_url,
                    format=get_file_extension_from_url_string(input_audio_url)
                )
            )
        )

    @classmethod
    def from_input_audio_file_path(cls, role: RoleLiteralStr, input_audio_file_path: Path | str) -> Self:
        with open(Path(input_audio_file_path), 'rb') as input_audio_file:
            return cls.from_input_audio_base64_string(
                role=role,
                input_audio_base64_string=input_audio_file.read().decode("base64")
            )

    @classmethod
    def from_input_audio_base64_string(cls, role: RoleLiteralStr, input_audio_base64_string: str) -> Self:
        return cls(
            role=role,
            content=MessageContent(
                type='input_audio',
                input_audio=InputAudio(
                    data=input_audio_base64_string,
                    format=get_audio_format_from_base64_string(input_audio_base64_string)
                )
            )
        )


class MessageHistory(BaseModel):
    messages: List[Message] = Field(default_factory=list)

    def __len__(self) -> int:
        return len(self.messages)

    def __getitem__(self, index: int) -> list[Message] | Message:
        return self.messages[index]

    def __iter__(self) -> Iterator[Message]:
        yield from self.messages

    def __setitem__(self, index: int, message: Message):
        self.messages[index] = message

    @property
    def estimated_token_count(self) -> int:
        return sum(message.estimated_token_count for message in self.messages)

    @property
    def has_system_message(self) -> bool:
        return len(self.messages) > 0 and self.messages[0].role == 'system'

    def create_message(
            self,
            role: RoleLiteralStr,
            text: str | None = None,
            image_urls: list[str] | None = None,
            image_file_paths: list[Path | str] | None = None,
            image_base64_strings: list[str] | None = None,
            input_audio_urls: list[str] | None = None,
            input_audio_file_paths: list[str] | None = None,
            input_audio_base64_strings: list[str] | None = None,
            prepend: bool = False,
    ) -> None:
        messages = []

        if text is not None:
            messages.append(Message.from_text(role=role, text=text))

        elif image_urls is not None or image_file_paths is not None or image_base64_strings is not None:
            for image_url in image_urls or []:
                messages.append(Message.from_image_url(role=role, image_url=image_url))

            for image_file_path in image_file_paths or []:
                messages.append(Message.from_image_file_path(role=role, image_file_path=image_file_path))

            for image_base64_data_encode in image_base64_strings or []:
                messages.append(
                    Message.from_image_base64_string(role=role, image_base64_string=image_base64_data_encode))

        elif input_audio_urls is not None or input_audio_file_paths is not None or input_audio_base64_strings is not None:
            for input_audio_url in input_audio_urls or []:
                messages.append(Message.from_input_audio_url(role=role, input_audio_url=input_audio_url))

            for input_audio_file_path in input_audio_file_paths or []:
                messages.append(
                    Message.from_input_audio_file_path(role=role, input_audio_file_path=input_audio_file_path))

            for input_audio_base64_data_encode in input_audio_base64_strings or []:
                messages.append(Message.from_input_audio_base64_string(role=role,
                                                                       input_audio_base64_string=input_audio_base64_data_encode))

        if prepend:
            self.prepend_messages(messages)
        else:
            self.append_messages(messages)

    def append_message(self, message: Message) -> None:
        self.messages.append(message)

    def append_messages(self, messages: list[Message]) -> None:
        self.messages.extend(messages)

    def prepend_message(self, message: Message) -> None:
        self.messages.insert(0, message)

    def prepend_messages(self, messages: list[Message]) -> None:
        self.messages = messages + self.messages

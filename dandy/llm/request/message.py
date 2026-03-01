import base64
from pathlib import Path
from typing import Iterator, List, Literal

from pydantic import BaseModel, Field

from dandy.file.audio.utils import get_audio_format_from_base64_string
from dandy.file.image.utils import get_image_mime_type_from_base64_string
from dandy.file.utils import get_file_extension_from_url_string
from dandy.llm.tokens.utils import get_estimated_token_count_for_string

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
        if self.type == 'text' and self.text:
            return self.text

        if self.type == 'image_url' and self.image_url:
            return self.image_url.__str__()

        if self.type == 'input_audio' and self.input_audio:
            return self.input_audio.as_data_encoded_base64()

        return self.__str__()


class Message(BaseModel):
    role: RoleLiteralStr
    content: list[MessageContent] = Field(default_factory=list)

    @property
    def estimated_token_count(self) -> int:
        return get_estimated_token_count_for_string(self.__str__())

    def add_content_from_text(self, text: str):
        self.content.append(
            MessageContent(type='text', text=text)
        )

    def add_content_from_image_url(self, image_url: str):
        self.content.append(
            MessageContent(type='image_url', image_url=ImageUrl(url=image_url))
        )

    def add_content_from_image_file_path(self, image_file_path: Path | str):
        with open(Path(image_file_path), 'rb') as image_file:
            self.add_content_from_image_base64_string(
                image_base64_string=base64.b64encode(
                    image_file.read()
                ).decode('utf-8')
            )

    def add_content_from_image_base64_string(self, image_base64_string: str):
        self.content.append(
            MessageContent(
                type='image_url',
                image_url=ImageUrl(
                    url=f'data:{get_image_mime_type_from_base64_string(image_base64_string)};base64,{image_base64_string}'
                )
            )
        )

    def add_content_from_input_audio_url(self, input_audio_url: str):
        self.content.append(
            MessageContent(
                type='input_audio',
                input_audio=InputAudio(
                    data=input_audio_url,
                    format=get_file_extension_from_url_string(input_audio_url)
                )
            )
        )

    def add_content_from_input_audio_file_path(self, input_audio_file_path: Path | str):
        with open(Path(input_audio_file_path), 'rb') as input_audio_file:
            self.add_content_from_input_audio_base64_string(
                input_audio_base64_string=base64.b64encode(
                    input_audio_file.read()
                ).decode('utf-8')
            )

    def add_content_from_input_audio_base64_string(self, input_audio_base64_string: str):
        self.content.append(
            MessageContent(
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
            prepend: bool = False,
    ) -> None:
        message = Message(role=role)

        if text is not None:
            message.add_content_from_text(text=text)

        for image_url in image_urls or []:
            message.add_content_from_image_url(
                image_url=image_url
            )

        for image_file_path in image_file_paths or []:
            message.add_content_from_image_file_path(
                image_file_path=image_file_path
            )

        for image_base64_string in image_base64_strings or []:
            message.add_content_from_image_base64_string(
                image_base64_string=image_base64_string
            )

        for audio_url in audio_urls or []:
            message.add_content_from_input_audio_url(
                input_audio_url=audio_url
            )

        for audio_file_path in audio_file_paths or []:
            message.add_content_from_input_audio_file_path(
                input_audio_file_path=audio_file_path
            )

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

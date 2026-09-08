import base64
from pathlib import Path
from typing import Iterator, Literal

from pydantic import BaseModel, Field

from dandy.file.audio.utils import get_audio_format_from_base64_string
from dandy.file.image.utils import get_image_mime_type_from_base64_string
from dandy.file.utils import get_file_extension_from_url_string
from dandy.llm.tokens.utils import (
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


class Message(BaseModel):
    role: RoleLiteralStr
    content: list[MessageContent] = Field(default_factory=list)
    tool_call_id: str | None = None
    tool_calls: list[dict] | None = None

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

    def add_content_from_text(self, text: str):
        self.content.append(MessageContent(type='text', text=text))

    def add_content_from_image_url(self, image_url: str):
        self.content.append(MessageContent(type='image_url', image_url=ImageUrl(url=image_url)))

    def add_content_from_image_file_path(self, image_file_path: Path | str):
        with open(Path(image_file_path), 'rb') as image_file:
            self.add_content_from_image_base64_string(
                image_base64_string=base64.b64encode(image_file.read()).decode('utf-8')
            )

    def add_content_from_image_base64_string(self, image_base64_string: str):
        self.content.append(
            MessageContent(
                type='image_url',
                image_url=ImageUrl(
                    url=f'data:{get_image_mime_type_from_base64_string(image_base64_string)};base64,{image_base64_string}'
                ),
            )
        )

    def add_content_from_input_audio_url(self, input_audio_url: str):
        self.content.append(
            MessageContent(
                type='input_audio',
                input_audio=InputAudio(
                    data=input_audio_url, format=get_file_extension_from_url_string(input_audio_url)
                ),
            )
        )

    def add_content_from_input_audio_file_path(self, input_audio_file_path: Path | str):
        with open(Path(input_audio_file_path), 'rb') as input_audio_file:
            self.add_content_from_input_audio_base64_string(
                input_audio_base64_string=base64.b64encode(input_audio_file.read()).decode('utf-8')
            )

    def add_content_from_input_audio_base64_string(self, input_audio_base64_string: str):
        self.content.append(
            MessageContent(
                type='input_audio',
                input_audio=InputAudio(
                    data=input_audio_base64_string,
                    format=get_audio_format_from_base64_string(input_audio_base64_string),
                ),
            )
        )


class MessageHistory(BaseModel):
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


def compact_message_history(history: MessageHistory, max_context_tokens: int) -> None:
    """Trim ``history`` until its estimated token count fits the budget.

    The system message and the newest message are always kept. Tool-use rounds
    (an assistant tool-call declaration plus its results) are dropped oldest
    first because they consume the most tokens, then oldest plain exchanges.

    Does not raise when the history cannot be brought under budget, it simply
    drops everything droppable.
    """
    per_message_token_counts = [message.estimated_token_count for message in history.messages]
    total_token_count = sum(per_message_token_counts)

    while total_token_count > max_context_tokens:
        start_index, end_index = _oldest_droppable_range(history)

        if start_index is None or end_index is None:
            return

        total_token_count -= sum(per_message_token_counts[start_index:end_index])

        del per_message_token_counts[start_index:end_index]
        del history.messages[start_index:end_index]


def _oldest_droppable_range(history: MessageHistory) -> tuple[int | None, int | None]:
    messages = history.messages

    if len(messages) < 2:
        return None, None

    last_index = len(messages) - 1

    for index in range(1, last_index):
        message = messages[index]

        if message.role != 'assistant' or not message.tool_calls:
            continue

        end_index = index + 1

        while end_index < len(messages) and messages[end_index].role == 'tool':
            end_index += 1

        return index, end_index

    for index in range(1, last_index):
        message = messages[index]

        if message.role == 'user':
            return index, index + 1

        if message.role == 'assistant' and not message.tool_calls:
            return index, index + 1

    return None, None

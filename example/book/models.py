from pathlib import Path

from typing_extensions import List, Any, Iterable

from pydantic import BaseModel

from dandy.conf import settings


class Chapter(BaseModel):
    title: str
    content: str


class Book(BaseModel):
    title: str
    author: str
    overview: str
    chapters: List[Chapter]

    def to_markdown(self, markdown_obj: Any | None = None, markdown_str: str = '', level: int = 2) -> str:
        if markdown_obj is None:
            markdown_obj = self.model_dump()

        if level > 6:
            level = 6

        if isinstance(markdown_obj, dict):
            for key, value in markdown_obj.items():
                markdown_str += f'{"#" * level} {key}\n\n'

                if isinstance(value, dict):
                    markdown_str = self.to_markdown(value, markdown_str, level + 1)

                elif isinstance(value, list):
                    for item in value:
                        markdown_str = self.to_markdown(item, markdown_str, level + 1)

                else:
                    markdown_str += f'{value}\n\n'

        elif isinstance(markdown_obj, Iterable):
            for item in markdown_obj:
                markdown_str = self.to_markdown(item, markdown_str, level)

        else:
            markdown_str += f'{markdown_obj}\n\n'

        return markdown_str

    def to_markdown_file(self):
        with open(Path(settings.BASE_PATH,  f'example_book.md'), 'w') as markdown:
            markdown.write(self.to_markdown())

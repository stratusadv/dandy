from pathlib import Path

from typing import List, Any, Iterable

from pydantic import BaseModel

from dandy.conf import settings
from dandy.core.utils import python_obj_to_markdown
from example.book.enums import BookTheme


class Chapter(BaseModel):
    title: str
    content: str


class Book(BaseModel):
    title: str
    author: str
    theme: BookTheme
    overview: str
    chapters: List[Chapter]

    def to_markdown_file(self):
        with open(Path(settings.BASE_PATH,  f'example_book.md'), 'w') as markdown:
            markdown.write(
                python_obj_to_markdown(self.model_dump())
            )

from pathlib import Path
from typing import List

from pydantic import BaseModel

from dandy.shared.conf import settings
from dandy.shared.utils import python_obj_to_markdown
from tests.application.example_project.book.enums import BookTheme


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
        with open(
            Path(settings.BASE_PATH, 'example_project_book.md'), 'w', encoding='utf-8'
        ) as markdown_file:
            markdown_file.write(python_obj_to_markdown(self.model_dump()))

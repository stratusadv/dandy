from typing_extensions import List

from pydantic import BaseModel, Field


class Chapter(BaseModel):
    title: str
    content: str


class Book(BaseModel):
    title: str
    author: str
    overview: str
    chapters: List[Chapter]

    

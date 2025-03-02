from typing_extensions import List

from pydantic import BaseModel, Field


class Chapter(BaseModel):
    number: int
    title: str


class Book(BaseModel):
    title: str
    overview: str
    chapters: List[Chapter] = Field(default_factory=list)
    author: str = 'Dandy McAuthor'

    

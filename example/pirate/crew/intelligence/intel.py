from typing import List

from pydantic import BaseModel

from example.pirate.crew.enums import CrewRole


class CrewMemberIntel(BaseModel):
    first_name: str
    last_name: str
    role: CrewRole
    description: str
    age: int
    name_of_hat: str


class CrewIntel(BaseModel):
    members: List[CrewMemberIntel]
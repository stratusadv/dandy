from typing import List

from pydantic import BaseModel

from example.pirate.crew.models import CrewMember


class Ship(BaseModel):
    name: str
    crew: int
    description: str
    crew_members: List[CrewMember]
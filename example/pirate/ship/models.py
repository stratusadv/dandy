from typing import Union

from typing_extensions import List

from pydantic import BaseModel

from example.pirate.crew.models import CrewMember


class Ship(BaseModel):
    name: str
    description: str
    crew_members: Union[List[CrewMember], None] =  None
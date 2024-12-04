from typing import Union

from typing_extensions import List

from pydantic import BaseModel

from example.pirate.crew.models import CrewMemberIntel


class ShipIntel(BaseModel):
    name: str
    description: str
    crew_members: Union[List[CrewMemberIntel], None] =  None
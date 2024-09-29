from pydantic import BaseModel

from example.pirate.crew.enums import CrewRole


class CrewMember(BaseModel):
    first_name: str
    last_name: str
    role: CrewRole
    description: str
    age: int
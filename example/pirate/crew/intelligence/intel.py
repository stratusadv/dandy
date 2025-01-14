from typing import List

from dandy.intel import Intel

from example.pirate.crew.enums import CrewRole


class CrewMemberIntel(Intel):
    first_name: str
    last_name: str
    role: CrewRole
    description: str
    age: int
    name_of_hat: str


class CrewIntel(Intel):
    members: List[CrewMemberIntel]
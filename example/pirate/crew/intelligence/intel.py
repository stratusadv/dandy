from typing_extensions import List

from dandy.intel import BaseIntel

from example.pirate.crew.enums import CrewRole


class CrewMemberIntel(BaseIntel):
    first_name: str
    last_name: str
    role: CrewRole
    description: str
    age: int
    name_of_hat: str
    coin_purse_amount: int
    blood_alcohol_level: float
    

class CrewIntel(BaseIntel):
    members: List[CrewMemberIntel]
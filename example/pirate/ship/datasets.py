from example.pirate.crew.models import CrewMember, CrewRole
from example.pirate.ship.models import Ship


QUEEN_ANNES_REVENGE = Ship(
    name="Queen Anne's Revenge",
    description="The Queen Anne's Revenge is the biggest ship in the world.",
    crew_members=[
        CrewMember(
            first_name='John',
            last_name='Doe',
            role=CrewRole.captain,
            description="The captain of the ship.",
            age=50
        )
    ]
)

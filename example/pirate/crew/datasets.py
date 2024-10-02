from example.pirate.crew.enums import CrewRole
from example.pirate.crew.models import CrewMember

CREW_MEMBERS = [
        CrewMember(
            first_name='John',
            last_name='Doe',
            role=CrewRole.captain,
            description="The captain of the ship.",
            age=50
        ),
        CrewMember(
            first_name='Frobulus',
            last_name='Faxanadoo',
            role=CrewRole.engineer,
            description="The captain of the ship.",
            age=50
        )
    ]
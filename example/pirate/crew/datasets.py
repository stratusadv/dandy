from example.pirate.crew.enums import CrewRole
from example.pirate.crew.models import CrewMemberIntel

CREW_MEMBERS = {
    'captain_1': CrewMemberIntel(
        first_name='Benjamin',
        last_name='Hornigold',
        role=CrewRole.CAPTAIN,
        description="A respected pirate who later became a privateer.",
        age=45
    ),
    'captain_2':CrewMemberIntel(
        first_name='Bartholomew',
        last_name='Roberts',
        role=CrewRole.CAPTAIN,
        description="One of the most successful pirates in history.",
        age=39
    ),

    'navigator_1': CrewMemberIntel(
        first_name='Frobulus',
        last_name='Faxanadoo',
        role=CrewRole.NAVIGATOR,
        description="Skilled in reading winds and currents.",
        age=50
    ),
    'navigator_2': CrewMemberIntel(
        first_name='Ned',
        last_name='Windbag',
        role=CrewRole.NAVIGATOR,
        description="Keeps a sharp eye on the stars and charts.",
        age=42
    ),
    
    'engineer_1': CrewMemberIntel(
        first_name='Sally',
        last_name='Seasight',
        role=CrewRole.ENGINEER,
        description="Expert at fixing any mechanical issue aboard the ship.",
        age=45
    ),
    'engineer_2': CrewMemberIntel(
        first_name='Quintus',
        last_name='Compassnose',
        role=CrewRole.ENGINEER,
        description="Never misses a detail in maintaining ship integrity.",
        age=52
    ),
}

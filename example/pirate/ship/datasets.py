from example.pirate.crew.datasets import CREW_MEMBERS
from example.pirate.ship.models import Ship

QUEEN_ANNES_REVENGE = Ship(
    name="Queen Annes Revenge",
    description="The Queen Annes Revenge is the biggest ship in the world.",
)

PIRATE_SHIPS = {
    'queen_annes_revenge': QUEEN_ANNES_REVENGE,
    'ghostly_galleon': Ship(
        name="Ghostly Galleon",
        description="The Ghostly Galleon is the spookiest ship in the world.",
    ),
    'ravens_roost': Ship(
        name="Ravens Roost",
        description="The ship with the most ravens on it in the world.",
    ),
}

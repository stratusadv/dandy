from example.pirate.crew.datasets import CREW_MEMBERS
from example.pirate.ship.models import ShipIntel

QUEEN_ANNES_REVENGE = ShipIntel(
    name="Queen Annes Revenge",
    description="The Queen Anne's Revenge is the biggest ship in the world.",
)

PIRATE_SHIPS = {
    'queen_annes_revenge': QUEEN_ANNES_REVENGE,
    'ghostly_galleon': ShipIntel(
        name="Ghostly Galleon",
        description="The Ghostly Galleon is the spookiest ship in the world.",
    ),
    'ravens_roost': ShipIntel(
        name="Ravens Roost",
        description="The ship with the most ravens on it in the world.",
    ),
}

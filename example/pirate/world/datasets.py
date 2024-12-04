from example.pirate.world.models import OceanIntel, IslandIntel

OCEANS = {
    "Pacific": OceanIntel(
        name="Pacific",
        description="The Pacific Ocean is the largest ocean in the world.",
        size=10_000_000,
        depth=100_000,
        islands=[
            IslandIntel(
                name="Mount Cook",
                description="The largest island in the Pacific Ocean.",
                size=100_000,
            ),
            IslandIntel(
                name="Tahiti",
                description="The smallest island in the Pacific Ocean.",
                size=10_000,
            ),
            IslandIntel(
                name="Hawaii",
                description="Another island in the Pacific Ocean.",
                size=50_000,
            )
        ],
    ),
    "Atlantic": OceanIntel(
        name="Atlantic",
        description="The Atlantic Ocean is the largest ocean in the world.",
        size=10_000_000,
        depth=100_000,
        islands=[
            IslandIntel(
                name="Bermuda",
                description="The largest island in the Atlantic Ocean.",
                size=100_000,
            ),
            IslandIntel(
                name="South Georgia",
                description="The smallest island in the Atlantic Ocean.",
                size=10_000,
            ),
            IslandIntel(
                name="Greenland",
                description="Another island in the Atlantic Ocean.",
                size=50_000,
            ),
        ],
    ),
}
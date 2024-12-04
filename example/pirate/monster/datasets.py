from example.pirate.monster.models import SeaMonsterIntel, SeaMonsterType

MONSTERS = {
    'kraken': SeaMonsterIntel(
        type=SeaMonsterType.KRAKEN
    ),
    'sea_serpent': SeaMonsterIntel(
        type=SeaMonsterType.SEA_SERPENT
    ),
    'leviathan': SeaMonsterIntel(
        type=SeaMonsterType.LEVIATHAN
    ),
    'hydra': SeaMonsterIntel(
        type=SeaMonsterType.HYDRA
    ),
    'cthulhu': SeaMonsterIntel(
        type=SeaMonsterType.CTHULHU
    ),
}
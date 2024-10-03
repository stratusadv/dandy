from example.pirate.monster.models import SeaMonster, SeaMonsterType

MONSTERS = {
    'kraken': SeaMonster(
        type=SeaMonsterType.KRAKEN
    ),
    'sea_serpent': SeaMonster(
        type=SeaMonsterType.SEA_SERPENT
    ),
    'leviathan': SeaMonster(
        type=SeaMonsterType.LEVIATHAN
    ),
    'hydra': SeaMonster(
        type=SeaMonsterType.HYDRA
    ),
    'cthulhu': SeaMonster(
        type=SeaMonsterType.CTHULHU
    ),
}
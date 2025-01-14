from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from dandy.llm import Prompt

if TYPE_CHECKING:
    from example.pirate.monster.intelligence.intel import SeaMonsterIntel
    from example.pirate.ship.intelligence.intel import ShipIntel
    from example.pirate.world.intelligence.intel import OceanIntel


def pirate_story_prompt(
        ocean: OceanIntel,
        ship: ShipIntel,
        sea_monster: SeaMonsterIntel
) -> Prompt:
    return (
        Prompt()
        .text('Create a pirate short story in the following ocean:')
        .intel(ocean, triple_quote=True)
        .line_break()
        .text('With the following ship:')
        .intel(ship, triple_quote=True)
        .line_break()
        .text('That has to face this sea monster:')
        .intel(sea_monster, triple_quote=True)
        .line_break()
        .random_choice([
            'At the end of the story the crew fails and dies.',
            'At the end of the story the crew meets a happy ending.',
            'At the end of the story there is a crazy twist involving space cowboys.',
        ])
    )

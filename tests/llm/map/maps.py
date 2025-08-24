from dataclasses import dataclass

from dandy.llm.config import LlmConfigOptions
from dandy.map.map import Map


class FunLlmMap(Map):
    mapping_keys_description = 'Personalities'
    mapping = {
        'someone that needs a laugh and needs clowns': 113,
        'someone is interested in seeing animals': 782,
        'someone looking for something more technical': 927,
        'someone who would be glad to get a free puppies': 391,
    }

class DragonLlmMap(Map):
    mapping_keys_description = 'Battle Outcomes'
    llm_config_options = LlmConfigOptions(temperature=0)
    mapping = {
        'The player is packing other stuff': 'The battle was lost',
        'The player brought a sword': 'The battle was won',
    }


class TreasureLlmMap(Map):
    mapping_keys_description: str = 'Treasure Outcomes'
    llm_config_options = LlmConfigOptions(temperature=0)
    mapping = {
        'Player brought a shovel': 'The treasure was recovered',
        'Player did not bring a shovel': 'The treasure was lost'
    }


class AdventureGameLlmMap(Map):
    mapping_keys_description = 'Adventure Direction Decisions'
    llm_config_options = LlmConfigOptions(temperature=0)
    mapping = {
        'The player travels down the path to the left': DragonLlmMap(),
        'The player goes right into the jungle': TreasureLlmMap()
    }


class NestedBirdMap(Map):
    llm_config_options = LlmConfigOptions(temperature=0)
    mapping_keys_description = 'Bird Descriptions'
    mapping = {
        'the bird is dark colored': Map(
            mapping_keys_description='Bird Sounds',
            mapping={
                'it is a crow': 'caw crow',
                'it is a raven': 'caw raven'
            }
        ),
        'the bird is colorful': Map(
            mapping_keys_description='Bird Sounds',
            mapping={
                'it is a parrot': 'caw parrot',
                'it is a parakeet': 'caw parakeet'
            }
        )
    }


mapping = {
    'I like tacos': {
        'cicken': 12,
        'beeeeef': 12,
    }
}

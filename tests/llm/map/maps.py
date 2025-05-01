from dandy.llm import LlmConfigOptions
from dandy.llm.map.llm_map import BaseLlmMap
from dandy.map.map import Map


class FunLlmMap(BaseLlmMap):
    map_keys_description = 'Personalities'
    map = Map({
        'someone that needs a laugh and needs clowns': 113,
        'someone is interested in seeing animals': 782,
        'someone looking for something more technical': 927,
        'someone who would be glad to get a free puppies': 391,
    })


class DragonLlmMap(BaseLlmMap):
    map_keys_description = 'Battle Outcomes'
    config_options = LlmConfigOptions(temperature=0)
    map = Map({
        'Player brought a sword': 'The battle was won',
        'Player did not bring a sword': 'The battle was lost'
    })


class TreasureLlmMap(BaseLlmMap):
    map_keys_description = 'Treasure Outcomes'
    config_options = LlmConfigOptions(temperature=0)
    map = Map({
        'Player brought a shovel': 'The treasure was recovered',
        'Player did not bring a shovel': 'The treasure was lost'
    })


class AdventureGameLlmMap(BaseLlmMap):
    map_keys_description = 'Adventure Decisions'
    config_options = LlmConfigOptions(temperature=0)
    map = Map({
        'The player goes left': DragonLlmMap,
        'The player goes right': TreasureLlmMap
    })


class NestedBirdMap(BaseLlmMap):
    config_options = LlmConfigOptions(temperature=0)
    map_keys_description = 'Bird Descriptions'
    map = Map({
        'the bird is dark colored': Map({
            'it is a crow': 'caw crow',
            'it is a raven': 'caw raven'
        }),
        'the bird is colorful': Map({
            'it is a parrot': 'caw parrot',
            'it is a parakeet': 'caw parakeet'
        })
    })


map = {
    'I like tacos': {
        'cicken': 12,
        'beeeeef': 12,
    }
}
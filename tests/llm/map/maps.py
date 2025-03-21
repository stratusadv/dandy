from dataclasses import dataclass

from dandy.llm import LlmConfigOptions
from dandy.llm.map.llm_map import BaseLlmMap


class FunLlmMap(BaseLlmMap):
    map = {
        'someone that needs a laugh and needs clowns': 113,
        'someone is interested in seeing animals': 782,
        'someone looking for something more technical': 927,
        'someone who would be glad to get a free puppies': 391,
    }


class DragonLlmMap(BaseLlmMap):
    config_options = LlmConfigOptions(temperature=0)
    map ={
        'Player brought a sword': 'The battle was won',
        'Player did not bring a sword': 'The battle was lost'
    }


class TreasureLlmMap(BaseLlmMap):
    config_options = LlmConfigOptions(temperature=0)
    map = {
        'Player brought a shovel': 'The treasure was revcovered',
        'Player did not bring a shovel': 'The treasure was lost'
    }


class AdventureGameLlmMap(BaseLlmMap):
    config_options = LlmConfigOptions(temperature=0)
    map = {
        'The player goes left': DragonLlmMap,
        'The player goes right': TreasureLlmMap
    }

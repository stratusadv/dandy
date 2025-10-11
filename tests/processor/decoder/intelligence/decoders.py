from dandy.llm.config.options import LlmConfigOptions
from dandy.processor.decoder.decoder import Decoder


class FunDecoder(Decoder):
    mapping_keys_description = 'Descriptions of People'
    mapping = {
        'Would be glad to get a free puppy': 391,
        'Needs a laugh and needs clowns': 113,
        'Interested in seeing animals': 782,
        'Looking for something more technical': 927,
    }

class DragonDecoder(Decoder):
    mapping_keys_description = 'Battle Outcomes'
    llm_config_options = LlmConfigOptions(temperature=0)
    mapping = {
        'The player is packing other stuff': 'The battle was lost',
        'The player brought a sword': 'The battle was won',
    }


class TreasureDecoder(Decoder):
    mapping_keys_description: str = 'Treasure Outcomes'
    llm_config_options = LlmConfigOptions(temperature=0)
    mapping = {
        'Brought a shovel': 'The treasure was recovered',
        'Did not bring a shovel': 'The treasure was lost'
    }


class AdventureGameDecoder(Decoder):
    mapping_keys_description = 'Adventure Direction Decisions'
    llm_config_options = LlmConfigOptions(temperature=0)
    mapping = {
        'The player travels down the path to the left': DragonDecoder(),
        'The player goes right into the jungle': TreasureDecoder()
    }


class NestedBirdDecoder(Decoder):
    llm_config_options = LlmConfigOptions(temperature=0)
    mapping_keys_description = 'Bird Descriptions'
    mapping = {
        'the bird is dark colored': Decoder(
            mapping_keys_description='Bird Sounds',
            mapping={
                'it is a crow': 'caw crow',
                'it is a raven': 'caw raven'
            }
        ),
        'the bird is colorful': Decoder(
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

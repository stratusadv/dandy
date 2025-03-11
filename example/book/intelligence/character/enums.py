from enum import Enum


class CharacterType(Enum):
    PROTAGONIST = 'Protagonist'
    ANTAGONIST = 'Antagonist'
    DEUTERAGONIST = 'Deuteragonist'
    TRITAGONIST = 'Tritagonist'
    LOVE_INTEREST = 'Love Interest'
    CONFIDANT = 'Confidant'
    FOIL = 'Foil'
    EXTRA = 'Extra'

    
class CharacterAlignment(Enum):
    GOOD = 'Good'
    NEUTRAL = 'Neutral'
    CHAOTIC = 'Chaotic'
    EVIL = 'Evil'
    
    

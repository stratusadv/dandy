import random

# The thinking phrase generator builds one phrase at a time by combining an
# action, a pocket-watch-era object, and an optional instrument (or folding
# shape / finishing quirk). The fragment lists below stay small on purpose:
# their cross product is what multiplies the number of possible phrases far
# beyond any static list. Object families keep the pairings from sounding
# absurd (no 'Polishing a Silk Cravat with a Tachyon Ruler'); an action that
# fits several families lists them all.

# Leading words that take 'an' by sound; the object names above are all
# article-free, so this list and `_article` keep the grammar right.
_AN_WORDS = ('opal', 'amber', 'ambergris', 'amethyst')

OBJECT_FAMILIES: dict[str, tuple[str, ...]] = {
    'fabric': (
        'Silk Cravat',
        'Linen Handkerchief',
        'Silk Scarf',
        'Pocket Square',
        'Monogrammed Handkerchief',
        'Velvet Cufflink',
        'Silted Waistcoat',
        'Tailcoat',
        'Silk Handkerchief',
        'Handkerchief',
    ),
    'gem': (
        'Diamond-Encrusted Cufflink',
        'Diamond-Studded Cane Tip',
        'Ruby-Encrusted Monocle',
        'Sapphire Fob',
        'Pearl-Buttoned Waistcoat',
        'Opal-Set Cufflink',
        'Amethyst Vinaigrette',
    ),
    'metal': (
        'Gold-Plated Cane',
        'Silver Cufflink',
        'Platinum Pocket Watch',
        'Brass Monocle',
        'Silver Snuff Box',
        'Silver Cigarette Case',
        'Signet Ring',
        'Pocket Compass',
        'Pocket Watch',
        'Monocle',
        'Monocle Chain',
        'Top Hat',
        'Silk-Top Hat',
        'Watch Chain',
        'Spats Buckle',
        'Cigar Case',
        'Cane',
        'Walking Stick',
        'Cane Tip',
        'Pocket Square',
    ),
}

_FOLD_SLOTS = (
    'a Perfect Origami Lotus',
    'a Swan',
    'a Tesseract Swan',
    'a Quantum Butterfly',
    'a Fractal Phoenix',
    'a Chroniton Rose',
    'a Möbius Strip',
    'a 4D Hypercube',
    'a Klein Bottle',
    'a Fractal Peacock',
    'a Gentle Wave',
)

_INSTRUMENT_SLOTS = {
    'brush': (
        'a Diamond-Encrusted Brush',
        'a Feather Duster',
        'a Quantum Feather Duster',
        'a Photon-Enhanced Brush',
        'a Singularity-Enhanced Duster',
        'a Nanobot Brush',
        'a Monogrammed Brush',
    ),
    'cloth': (
        'a Velvet Cloth',
        'a Quantum-Enhanced Microfiber',
        'a Microfiber Cloth',
        'a Monogrammed Cloth',
        'a Silk-Trimmed Cloth',
    ),
    'polish': (
        'Neutronium Polish',
        'Void Polish',
        'Antimatter Polish',
        'Chroniton Polish',
        'Liquid Diamond Polish',
        'Liquid Stardust',
        'Liquid Time',
        'Nebula Dust',
    ),
    'scent': (
        'Scented Dark Matter',
        'Nebula-Scented Nanoparticles',
        'Essence of Distant Galaxies',
        'Antimatter Scent Oil',
        'Bergamot',
        'Ambergris',
        'Sandalwood',
        'Cedar',
        'Lavender',
        'Rare Orchid Essence',
        'Chroniton Scent',
    ),
    'ruler': (
        'a Quantum Ruler',
        'a Chroniton Ruler',
        'a Tachyon Ruler',
        'a Graviton Ruler',
        'a Non-Euclidean Protractor',
        'a Holographic Protractor',
        'a Singularity Protractor',
        'Calipers',
        'a Multidimensional Caliper',
        'a Tensiometer',
    ),
    'scope': (
        'a Quantum Microscope',
        'a Tachyon Scanner',
        'a Singularity Scanner',
        'a Multiverse Scanner',
        'a Holographic Projector',
        'a Loupe',
        'a Magnifier',
        'a DNA-Scanning Loupe',
        'a Singularity Wrench',
        'a Temporal Micro-Adjuster',
        'a Chroniton Emitter',
        'a Multiverse Calibration Tool',
    ),
    'vessel': (
        'a Crystal Glass',
        'a Gold-Plated Snifter',
        'a Silver Goblet',
        'a Chroniton-Infused Vessel',
        'a Nebula Goblet',
        'an Event Horizon Chalice',
        'a Celestial Chalice',
    ),
    'fluff': (
        'a Feather',
        'Anti-Gravity Puffs',
        'Quantum Fluff',
        'a Warp-Field Micro-Airbrush',
        'a Micro-Airbrush',
    ),
    'file': ('a Micro-File', 'Diamond-Encrusted Nanofiles', 'a Chroniton File', 'Diamond Dust'),
}

_INSTRUMENT_SLOT_BY_FAMILY = {
    'fabric': ('brush', 'cloth', 'scent', 'fluff', 'scope'),
    'gem': ('brush', 'cloth', 'polish', 'scent'),
    'metal': ('ruler', 'scope', 'vessel', 'file', 'polish'),
}

QUIRK_SLOTS = (
    'with Nanometer Precision',
    'with a Reality-Warping Flourish',
    'with a Gravity-Defying Flourish',
    'via Quantum Resonance',
    'with Approval',
    'Rhythmically',
    'Thoughtfully',
    'with both hands',
    'with Pinky Extended',
    'Precisely',
)

_ACTIONS: dict[str, tuple[tuple[str, ...], str, tuple[str, ...]]] = {
    'Adjusting': (('fabric',), 'instrument', ('brush',)),
    'Calibrating': (('metal',), 'instrument', ('scope', 'ruler')),
    'Counting': (('fabric',), 'instrument', ('scope',)),
    'Dabbing': (('fabric', 'gem'), 'instrument', ('scent', 'cloth')),
    'Dusting': (('fabric',), 'instrument', ('brush',)),
    'Examining': (('metal',), 'instrument', ('scope',)),
    'Filing': (('gem', 'metal'), 'instrument', ('file',)),
    'Fluffing': (('fabric',), 'instrument', ('fluff', 'brush')),
    'Folding': (('fabric',), 'fold', ()),
    'Infusing': (('fabric',), 'instrument', ('scent',)),
    'Inspecting': (('metal',), 'instrument', ('scope',)),
    'Polishing': (('gem', 'metal'), 'instrument', ('cloth',)),
    'Scenting': (('fabric',), 'instrument', ('scent',)),
    'Straightening': (('fabric', 'metal'), '', ()),
    'Stroking': (('fabric',), '', ()),
    'Tapping': (('metal',), '', ()),
    'Tuning': (('metal',), 'instrument', ('scope', 'ruler')),
    'Twirling': (('metal',), '', ()),
    'Unfurling': (('fabric',), '', ()),
}


def _article(name: str) -> str:
    first_word = name.lower().split(' ')[0].split('-')[0]

    return 'an' if first_word in _AN_WORDS else 'a'


def _object_phrase(family: str) -> str:
    name = random.choice(OBJECT_FAMILIES[family])

    return f'{_article(name)} {name}'


def thinking_phrase() -> str:
    """Generate one random thinking phrase from the sentence fragments."""
    verb = random.choice(list(_ACTIONS))
    families, slot_kind, slot_names = _ACTIONS[verb]
    family = random.choice(families)
    phrase = f'{verb} {_object_phrase(family).rstrip()}'

    if slot_kind == 'fold':
        phrase += f' into {random.choice(_FOLD_SLOTS)}'
    elif slot_kind == 'instrument' and random.random() < 0.7:
        slot = _INSTRUMENT_SLOTS[random.choice(slot_names)]
        phrase += f' with {random.choice(slot)}'

    if random.random() < 0.25:
        phrase += f' {random.choice(QUIRK_SLOTS)}'

    return phrase

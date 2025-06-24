from dandy.llm import BaseLlmMap, Map


class MuseumSubjectLlmMap(BaseLlmMap):
    map_keys_description = 'Colors of Museum Subjects'
    description = 'Matches colors to figure out which subject to learn in a museum.'
    map = Map({
        'green': 'Dinosaurs',
        'red': 'Birds',
        'blue': 'Fishes',
        'yellow': 'Reptiles',
        'purple': 'Monkeys',
    })

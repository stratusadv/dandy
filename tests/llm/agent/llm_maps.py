from dandy.map import Map


class MuseumSubjectLlmMap(Map):
    mapping_keys_description = 'Colors of Museum Subjects'
    description = 'Matches colors to figure out which subject to learn in a museum.'
    mapping = {
        'green': 'Dinosaurs',
        'red': 'Birds',
        'blue': 'Fishes',
        'yellow': 'Reptiles',
        'purple': 'Monkeys',
    }

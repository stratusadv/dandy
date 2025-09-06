from dandy.processor.map.map import Map


class MuseumSubjectMap(Map):
    mapping_keys_description = 'Colors of Museum Subjects'
    description = 'Matches colors to figure out which subject to learn in a museum.'
    mapping = {
        'green': 'Dinosaurs',
        'red': 'Birds',
        'blue': 'Fishes',
        'yellow': 'Reptiles',
        'purple': 'Monkeys',
    }

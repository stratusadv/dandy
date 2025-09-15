from dandy import Map

class AnimalFamilyMap(Map):
    mapping_keys_description = 'Animal Sounds'
    mapping = {
        'barking': 'dog',
        'meowing': 'cat',
        'quacking': 'duck'
    }

animal_families = AnimalFamilyMap().process(
    'I was out on a walk and heard some barking', 
    max_return_values=1
)

print(animal_families[0])

# Output: dog
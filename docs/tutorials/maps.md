# LLM Map

## Making Decisions

Making choices and decisions is a core part of any intelligence system and we wanted to make that as easy as possible.
The `LlmMap` can be used to make decisions or navigate choices with minimal configuration or code.

## Basic LLM Map

Here is a simple example of how to create a map using the `BaseLlmMap` that returns the family of an animal.
Maps always return a list of values and this can be controlled by the `choice_count` argument which defaults to 1.

```python exec="True" source="above" source="material-block" session="map"
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
```

## Advanced LLM Map

Maps can also be nested indefinitely and link to any value you want.
While a map is traversing if it comes across another `LlmMap` or `Map` it will continue to traverse to get the values nested within.

```python exec="True" source="above" source="material-block" session="map"
from dandy import Map

class MathBook:
    def __str__(self):
        return 'Math Book'

golf = 'Golf'

class LearningMap(Map):
    mapping_keys_description = 'Learning Subjects'
    mapping = {
        'history': 'Social Studies Book',
        'science': 'Laboratory Book',
        'numbers': MathBook()
    }

class ActivityMap(Map):
    mapping_keys_description = 'Physical Activities'
    mapping = {
        'running around outdoors': Map(
            mapping_keys_description='Activities',
            mapping={
            'throwing': 'Ball',
            'flinging': 'Frisbee',
            'walking': golf
        }),
        'playing with friends': Map(
            mapping_keys_description='Activities',
            mapping={
            'kicking': 'soccer',
            'swinging': 'baseball',
            'climbing': 'jungle gym'    
        }),
        'being inside': Map(
            mapping_keys_description='Activities',
            mapping={
            'logic': 'board game',
            'thinking': 'chess',
            'creative': 'painting'
        }),
        'learning more': LearningMap(),
        'no valid choice': None
    }
    
activities = ActivityMap().process(
    'Getting more education with something fun like numbers is what I like to do'
)

for activity in activities:
    print(activity)
```

!!! note

    All the examples are mostly using strings for values, but map values can be any type of 
    object so that you can get really creative when making maps.
# LLM Map

## Making Decisions

Making choices and decisions is a core part of any intelligence system and we wanted to make that as easy as possible.
The `LlmMap` can be used to make decisions or navigate choices with minimal configuration or code.

## Basic LLM Map

Here is a simple example of how to create a map using the `BaseLlmMap` that returns the family of an animal.
Maps always return a list of values and this can be controlled by the `choice_count` argument which defaults to 1.

```python exec="True" source="above" source="material-block" session="map"
from dandy.llm import BaseLlmMap, Map

class AnimalFamilyMap(BaseLlmMap):
    map = Map({
        'barking': 'dog',
        'meowing': 'cat',
        'quacking': 'duck'
    })
    
animal_families = AnimalFamilyMap.process('I was out on a walk and heard some barking', choice_count=1)

print(animal_families[0])
```

## Advanced LLM Map

Maps can also be nested indefinitely and link to any value you want.
While a map is traversing if it comes across another `LlmMap` or `Map` it will continue to traverse to get the values nested within.

```python exec="True" source="above" source="material-block" session="map"
from dandy.llm import BaseLlmMap, Map

class LearningMap(BaseLlmMap):
    map = Map({
        'history': 'Social Studies Book',
        'science': 'Laboratory Book',
        'numbers': 'Math Book'
    })

class ActivityMap(BaseLlmMap):
    map = Map({
        'running around outdoors': Map({
            'throwing': 'Ball',
            'flinging': 'Frisbee',
            'walking': 'Golf'
        }),
        'playing with friends': Map({
            'kicking': 'soccer',
            'swinging': 'baseball',
            'climbing': 'jungle gym'    
        }),
        'being inside': Map({
            'logic': 'board game',
            'thinking': 'chess',
            'creative': 'painting'
        }),
        'learning more': LearningMap
    })
    
activities = ActivityMap.process('Getting more education with something fun like numbers is what I like to do')

print(activities[0])
```

!!! note

    All the examples are using strings for values in the map for simplicty, 
    but maps can be used with any type of object so that you can get really creative when making maps.
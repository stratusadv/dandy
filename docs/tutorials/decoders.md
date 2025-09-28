# Decoder

## Making Decisions

Making choices and decisions is a core part of any intelligence system, and we wanted to make that as easy as possible.
The `Decoder` can be used to make decisions or navigate choices with minimal configuration or code.

## Basic Decoder

Here is a simple example of how to create a `Decoder` that returns the family of an animal.
Decoders always return a list of values, and this can be controlled by the `choice_count` argument which defaults to 1.

```python exec="True" source="above" source="material-block" session="decoder"
from dandy import Decoder

class AnimalFamilyDecoder(Decoder):
    mapping_keys_description = 'Animal Sounds'
    mapping = {
        'barking': 'dog',
        'meowing': 'cat',
        'quacking': 'duck'
    }
    
animal_families = AnimalFamilyDecoder().process(
    'I was out on a walk and heard some barking', 
    max_return_values=1
)

print(animal_families[0])
```

## Advanced Decoder

Decoders can also be nested indefinitely and link to any value you want.
While a decoder is traversing if it comes across another `Decoder` it will continue to traverse to get the values nested within.

```python exec="True" source="above" source="material-block" session="decoder"
from dandy import Decoder

class MathBook:
    def __str__(self):
        return 'Math Book'

golf = 'Golf'

class LearningDecoder(Decoder):
    mapping_keys_description = 'Learning Subjects'
    mapping = {
        'history': 'Social Studies Book',
        'science': 'Laboratory Book',
        'numbers': MathBook()
    }

class ActivityDecoder(Decoder):
    mapping_keys_description = 'Physical Activities'
    mapping = {
        'running around outdoors': Decoder(
            mapping_keys_description='Activities',
            mapping={
            'throwing': 'Ball',
            'flinging': 'Frisbee',
            'walking': golf
        }),
        'playing with friends': Decoder(
            mapping_keys_description='Activities',
            mapping={
            'kicking': 'soccer',
            'swinging': 'baseball',
            'climbing': 'jungle gym'    
        }),
        'being inside': Decoder(
            mapping_keys_description='Activities',
            mapping={
            'logic': 'board game',
            'thinking': 'chess',
            'creative': 'painting'
        }),
        'learning more': LearningDecoder(),
        'no valid choice': None
    }
    
activities = ActivityDecoder().process(
    'Getting more education with something fun like numbers is what I like to do'
)

for activity in activities:
    print(activity)
```

!!! note

    All the examples are mostly using strings for values, but `Decoder.mapping` values can be any type of 
    object so that you can get really creative when making decoders.
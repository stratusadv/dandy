# Intel

## Creating Intel

In Dandy we use an object called `Intel` to represent the information about objects in your project.

Let's go ahead and create a `ClownIntel` class that inherits from the `BaseIntel` class.

```python exec="True" source="above" source="material-block" session="intel"
from dandy.intel import BaseIntel

class ClownIntel(BaseIntel):
    clown_name: str
    can_juggle: bool
    real_name: str | None = None

bozo = ClownIntel(
    clown_name='Bozo', 
    can_juggle=True
)

print(bozo.can_juggle)
```

!!! note

    On the class `ClownIntel` we may not know the real name of the clown, which is why we set `real_name` to be optional.
    This is important as all `Intel` objects are type validated and would raise an error if the `real_name` were not set.

## Using Intel

Now that we have a `ClownIntel` object, let's use it with the `LlmBot` to generate a new clown.

The `process` method of the `LlmBot` will return an `Intel` object based on the `intel_class` argument.

```python exec="True" source="above" source="material-block" session="intel"
# Using ClownIntel from earlier

from dandy.llm import LlmBot

new_clown = LlmBot.process(
    prompt='Can you please generate me a clown, I am scared of jugglers!',
    intel_class=ClownIntel
)

print(new_clown)
```

## List Intel

Let's say we want to create a list of `ClownIntel` objects and still have all the support of the `BaseIntel` class.

We can use the `BaseListIntel` class to do that.

```python exec="True" source="above" source="material-block" session="intel"
# Using ClownIntel from earlier

from dandy.intel import BaseListIntel

class ClownListIntel(BaseListIntel):
    items: list[ClownIntel]

clowns_intel = ClownListIntel(items=[
    ClownIntel(clown_name='Bozo', can_juggle=True),
    ClownIntel(clown_name='Bimbo', can_juggle=False),    
    ClownIntel(clown_name='Bongo', can_juggle=True),
])

clowns_intel.append(ClownIntel(clown_name='Bubba', can_juggle=True))

print(len(clowns_intel))

for clown_intel in clowns_intel:
    print(clown_intel)
```

## Include and Exclude Fields

In the `process` method of the `LlmBot` class we can now include and exclude fields from the `Intel` object.

```python exec="True" source="above" source="material-block" session="intel"
# Using ClownIntel from earlier

another_clown = LlmBot.process(
    prompt='I am a big fan of juggling, can you please create me a clown!',
    intel_class=ClownIntel,
    exclude_fields={'real_name'},
)

print(another_clown)
```

You can also get the same result by including both the `can_juggle` and `clown_name` fields.

```python exec="True" source="above" source="material-block" session="intel"
# Using ClownIntel from earlier

another_clown = LlmBot.process(
    prompt='I am a big fan of juggling, can you please create me a clown!',
    intel_class=ClownIntel,
    include_fields={'can_juggle', 'clown_name'},
)

print(another_clown)
```

!!! warning

    All non-optional/required fields must be included either through excluding optional fields or manually including required fields.

## Advanced Intel

The `Intel` class is designed to provide lots of customization and control over your data.

Take a look at the next ...

```python exec="True" source="above" source="material-block" session="intel"
from enum import Enum


class Color(Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'


class HatIntel(BaseIntel):
    color: Color
    diameter: float
    has_feather: bool
    name: str | None = None


class ParrotIntel(BaseIntel):
    nick_name: str
    color: Color


class PirateIntel(BaseIntel):
    first_name: str
    last_name: str
    hat: HatIntel
    parrot: ParrotIntel | None = None


new_pirate = LlmBot.process(
    prompt='Can you please generate me a pirate?',
    intel_class=PirateIntel
)

print(new_pirate.hat.color)
```

## Advanced Include and Exclude Fields

Now that we have a more complex `PirateIntel` object, let's see how we can include and exclude fields while still getting a valid `PirateIntel` object.

We do this by creating a more complex `IncEx`/`Dict` object where the keys are the field names and the values are either `True` or a `Dict` of that child objects field names.

```python exec="True" source="above" source="material-block" session="intel"
# Using PirateIntel from earlier

new_pirate = LlmBot.process(
    prompt='Can you please generate me a pirate?',
    intel_class=PirateIntel,
    exclude_fields={'parrot': True, 'hat': {'name': True}},
)

print(new_pirate.hat.color)
```
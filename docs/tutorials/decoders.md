# Decoder

## Making Decisions

Making choices and decisions is a core part of any intelligence system, and we wanted to make that as easy as possible.
The decoder service (accessible via `Bot().llm.decoder`) can be used to make decisions or navigate choices with minimal configuration or code.

## Basic Decoder

Here is a simple example of how to use the decoder to return the family of an animal.
The decoder uses a prompt, keys description, and keys/values mapping to make decisions.

```python exec="True" source="above" source="material-block" session="decoder"
from dandy import Bot

bot = Bot()

keys_description = 'Animal Sounds'
keys_values = {
    'barking': 'dog',
    'meowing': 'cat',
    'quacking': 'duck'
}

animal_family = bot.llm.decoder.prompt_to_value(
    prompt='I was out on a walk and heard some barking',
    keys_description=keys_description,
    keys_values=keys_values
)

print(animal_family)
```

## Multiple Values

You can also request multiple values to be returned using `prompt_to_values` with `max_return_values`:

```python exec="True" source="above" source="material-block" session="decoder"
from dandy import Bot

bot = Bot()

keys_description = 'Activities'
keys_values = {
    'running': 'Sports',
    'reading': 'Learning',
    'coding': 'Technology',
    'painting': 'Art'
}

activities = bot.llm.decoder.prompt_to_values(
    prompt='I like running, reading books, and coding on my computer',
    keys_description=keys_description,
    keys_values=keys_values,
    max_return_values=3
)

for activity in activities:
    print(activity)
```

!!! note

    The decoder's keys_values dictionary can contain any type of object as values,
    allowing you to map to complex objects, not just strings.
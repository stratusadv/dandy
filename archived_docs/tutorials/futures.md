# Futures

## Easy Async

Futures are a powerful tool in Dandy that allow you to run code asynchronously which is great for non-blocking calls like network requests.

All you need to do on any class that has a `process` method is to call the `process_to_future` method instead.

### Without Async Futures

Let's run three `LlmBot.process` calls at once and see how long it takes.

```python exec="True" source="above" source="material-block" result="markdown" session="futures"
from time import perf_counter
from dandy import Bot

start_time = perf_counter()

pants_intel = Bot().process('What type of pants should I wear in the rain?')
shirt_intel = Bot().process('What type of shirt should I wear in the sun?')
shoes_intel = Bot().process('What type of shoes should I wear in the mud?')

print('Pants: ' + pants_intel.text)
print('Shirt: ' + shirt_intel.text)
print('Shoes: ' + shoes_intel.text)

print(f'Finished in {perf_counter() - start_time:.3f} seconds')
```

### With Async Futures

Now let's run with futures, note you have to access the `result` attribute of the futures to get to the returned value.

!!! warning

    We recommend you postfix your futures with `_future` to avoid naming conflicts and confusion.

```python exec="True" source="above" source="material-block" result="markdown" session="futures"
from time import perf_counter
from dandy import Bot

start_time = perf_counter()

pants_intel_future = Bot().process_to_future('What type of pants should I wear in the rain?')
shirt_intel_future = Bot().process_to_future('What type of shirt should I wear in the sun?')
shoes_intel_future = Bot().process_to_future('What type of shoes should I wear in the mud?')

print('Pants: ' + pants_intel_future.result.text)
print('Shirt: ' + shirt_intel_future.result.text)
print('Shoes: ' + shoes_intel_future.result.text)

print(f'Finished in {perf_counter() - start_time:.3f} seconds')
```

## Advanced Async

Sometimes in more complex situations you might need to cancel a future or set a timeout.

```python exec="True" source="above" source="material-block" result="markdown" session="futures"

from dandy import Bot

user_likes_scary_animals = True

cute_animal_future = Bot().process_to_future('Can you tell me about a random cute animal?')

scary_animal_future = Bot().process_to_future('Can you tell me about a random scary animal?')
scary_animal_future.set_timeout(seconds=30)

if user_likes_scary_animals:
    cute_animal_future.cancel()

print(scary_animal_future.result.text)
```
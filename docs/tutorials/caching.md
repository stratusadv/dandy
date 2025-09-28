# Caching

## What is Caching?

Caching is a technique used to speed up the execution of a function by storing the result of the function call.

The `@cache_to_memory` or `@cache_to_sqlite` decorator is used to cache the result of a function call.

!!! warning

    The caching system in Dandy is designed for performance and when it comes to cache keys it prioritizes speed.
    In very complex situations Dandy may fail to generate a proper caching key which will prevent caching.
    This is an extreme situation that will un likely affect most projects.
    

## Adding Caching

Let's make ourselves a `Decoder` and add `@cache_to_memory` to the `process` method.

```python exec="True" source="above" source="material-block" result="markdown" session="caching"
from time import perf_counter

from dandy import Decoder, cache_to_memory


class NumberDecoder(Decoder):
    mapping_keys_description = 'Verbose Number Descriptions'
    mapping = {
        'small numbers': 1,
        'medium numbers': 30,
        'large numbers': 100,
        'over 9000 numbers': 9002,
    }
    
    @cache_to_memory()
    def process(self, *args, **kwargs):
        return super().process(*args, **kwargs)
    
number_decoder = NumberDecoder()

start_time = perf_counter()

print(number_decoder.process('I really like dragon ball z')[0])

uncached_finish_time = perf_counter() - start_time

print(f'Finished uncached in {uncached_finish_time:.5f} seconds')

print(number_decoder.process('I really like dragon ball z')[0])
    
cached_finish_time = perf_counter() - start_time - uncached_finish_time

print(f'Finished cached in {cached_finish_time:.5f} seconds')

```

!!! tip

    The Dandy cache decorators can be used on any method or function with in your project as long as the arguments are serializable and the return type is serializable.

## Cache Settings

### Decorator Arguments

The `cache_to_memory` and `cache_to_sqlite` decorators can take `cache_name` and `limit` arguments.

This allows you to set separate caches and limits for individual methods and functions or group caches strategically.

In the example below all the add functions are cached into a memory cache called `add` which is stored in a sqlite database called `dandy_cache.db` with a row limit of 9,999,999.

```python exec="True" source="above" source="material-block" result="markdown" session="caching"
from dandy import cache_to_sqlite

@cache_to_sqlite(cache_name='add', limit=9_999_999)
def add(a, b):
    return a + b

print(add(3567, 5434)) # this will cache 1 entry in the sqlite database
```

### dandy_settings.py

You can configure your settings in your `dandy_settings.py` file to better control the cache settings by creating safe default values.

```python exec="True" source="above" source="material-block" result="markdown" session="caching"
from dandy.conf import settings

print(f'Cache Memory Limit: {settings.CACHE_MEMORY_LIMIT}') # Amount of items to keep in memory cache
print(f'Cache SQLite Path: {settings.CACHE_SQLITE_DATABASE_PATH}') # Path to sqlite database
print(f'Cache SQLite Limit: {settings.CACHE_SQLITE_LIMIT}') # Amount of items to keep in sqlite cache
```

!!! warning

    Make sure to pay very close attention to the values your caching and the limits you set as caching can get very system intensive.

## Advanced Caching

You can directly use the cache in your project as well to control the flow of caching.

Below we are going to use the `MemoryCache` and `generate_hash_key` functions to cache the results of the `do_math` function.

```python exec="True" source="above" source="material-block" result="markdown" session="caching"
from time import perf_counter

from dandy import MemoryCache, generate_cache_key


def do_math(a, b, c):
    sqlite_cache = MemoryCache(
        cache_name='more_math',
        limit=9_999_999
    )

    cache_key = generate_cache_key(do_math, a, b, c)
    
    number = sqlite_cache.get(
        cache_key
    )

    if number:
        return number

    number = 0
    for i in range(99_999_999):
        number += a + b + c

    sqlite_cache.set(
        cache_key,
        number
    )
    
    return number

start_time = perf_counter()

print(do_math(1, 4, 9))

uncached_finish_time = perf_counter() - start_time

print(f'Finished uncached in {uncached_finish_time:.5f} seconds')

print(do_math(1, 4, 9))
    
cached_finish_time = perf_counter() - start_time - uncached_finish_time

print(f'Finished cached in {cached_finish_time:.5f} seconds')

```

## Complex Caching

Now that we are comfortable with caching let's take a look at how we can manage the caches.

In the example below we have two caches `add` and `subtract` that are both stored in a sqlite database called `dandy_cache.db`.

```python exec="True" source="above" source="material-block" result="markdown" session="caching"
from dandy import SqliteCache, cache_to_sqlite, generate_cache_key

@cache_to_sqlite(cache_name='add', limit=100)
def add(a, b):
    return a + b
    
@cache_to_sqlite(cache_name='subtract', limit=100)
def subtract(a, b):
    return a - b

add_number = add(3, 5)
subtract_number = subtract(6, 7)

# instances of the cache singletons to manage each cache individually
sqlite_add_cache = SqliteCache(cache_name='add', limit=100)
sqlite_subtract_cache = SqliteCache(cache_name='subtract', limit=100)

add_hash_key = generate_cache_key(add, 3, 5)
subtract_hash_key = generate_cache_key(subtract, 6, 7)


print('Both `add` and `subtract` are cached')
print(f'>>> {sqlite_add_cache.get(add_hash_key)}')
print(f'>>> {sqlite_subtract_cache.get(subtract_hash_key)}')

SqliteCache.clear('add')

print('the `add` cache is cleared')
print(f'>>> {sqlite_add_cache.get(add_hash_key)}')
print(f'>>> {sqlite_subtract_cache.get(subtract_hash_key)}')

SqliteCache.clear_all()

print('All caches are cleared')
print(f'>>> {sqlite_add_cache.get(add_hash_key)}')
print(f'>>> {sqlite_subtract_cache.get(subtract_hash_key)}')

SqliteCache.destroy_all()

print('Sqlite database is deleted')

```
    
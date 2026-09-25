# Caching

**Domain concept:** [Cache and cache key](../domain_model/glossary.md#glossary) — a
generic memoization capability that knows nothing about LLMs.

**Lives in:** `dandy/infrastructure/cache/`.

## The decorator

```python
from dandy import cache_to_memory

call_count = 0


@cache_to_memory('demo_cache')
def fetch_thing(name: str) -> str:
    global call_count
    call_count += 1
    return f'fetched {name}'


fetch_thing('bozo')   # computes
fetch_thing('bozo')   # served from cache
print(call_count)     # 1
```

(Verified: the function body runs once; the second call is a cache hit.)

- `@cache_to_memory(name)` — an in-process `MemoryCache` (an LRU-bounded ordered dict).
- `@cache_to_sqlite(name)` — a persistent `SqliteCache` at
  `CACHE_SQLITE_DATABASE_PATH`.
- While a recording is live, a cache hit records a "Cached Response" event — you can see
  in a report that an LLM call was *not* made.

## Cache keys

`generate_cache_key` derives the key from the function identity (module + qualname) and a
hash of its arguments. The argument hashing is **layered and depth-capped**
(`CACHE_KEY_HASH_LAYER_LIMIT = 3`): nested structures are hashed recursively, but only
three layers deep — deeper hashing would pull in object state you did not mean to
key on.

Notable keying behaviors:

- `BaseIntel` / pydantic values hash by their JSON schema or dumped value, so
  semantically equal Intel key identically.
- Framework services hash by **class qualname**, detected structurally (by the
  `recorder_event_id` attribute) — the cache never imports them, which is how it stays a
  generic capability.
- Unhashable arguments raise `CacheCriticalError` with the object named.

## Manual use

```python
from dandy import MemoryCache

cache = MemoryCache(cache_name='demo_cache', limit=10)
cache.set('key', 'value')
cache.get('key')
cache.clean()
MemoryCache.clear_all()
```

# Infrastructure Layer

Infrastructure is where the framework meets the outside world: OpenAI-compatible LLM
endpoints over HTTP, the filesystem, SQLite, the thread pool, and the recorder that
persists event logs. Every adapter implements a seam from the
[shared kernel](shared.md) (a service or a connector) so the domain never learns which
endpoint, disk, or database it is running against.

The infrastructure layer may depend on the [domain](domain.md) and the [shared
kernel](shared.md). It may not import from `application` or `interfaces` except at the
few documented seams.

## LLM

::: dandy.infrastructure.llm.config.LlmConfig
    options:
        members:
            - generate_request_body
            - get_response_content
            - get_settings_value
            - reset

::: dandy.infrastructure.llm.connector.LlmConnector
    options:
        members:
            - prompt_to_intel
            - retry_request_to_intel
            - reset

## HTTP

::: dandy.infrastructure.http.connector.HttpConnector
    options:
        members:
            - request_to_response

::: dandy.infrastructure.http.service.HttpService
    options:
        members:
            - get
            - post
            - request_intel_to_response_intel
            - reset

::: dandy.infrastructure.http.mixin.HttpServiceMixin

::: dandy.infrastructure.http.url.Url

::: dandy.infrastructure.http.intelligence.intel

::: dandy.infrastructure.http.exceptions

## File

::: dandy.infrastructure.file.service.FileService
    options:
        members:
            - append
            - exists
            - make_directory
            - mkdir
            - read
            - remove
            - remove_directory
            - rm
            - write
            - reset

::: dandy.infrastructure.file.mixin.FileServiceMixin

## Cache

[Caching](../user_guide/caching.md): the abstract cache, the in-memory and SQLite
implementations, the key generator, and the decorators.

::: dandy.infrastructure.cache.cache.BaseCache

::: dandy.infrastructure.cache.memory.cache.MemoryCache

::: dandy.infrastructure.cache.sqlite.cache.SqliteCache

::: dandy.infrastructure.cache.sqlite.connection.SqliteConnection

::: dandy.infrastructure.cache.tools
    options:
        members:
            - generate_cache_key
            - convert_to_hashable_str

::: dandy.infrastructure.cache.memory.decorators.cache_to_memory

::: dandy.infrastructure.cache.sqlite.decorators.cache_to_sqlite

## Recorder

[Recording](../user_guide/recording.md): the event model, the singleton recorder, the
recording container, and the renderers (HTML / JSON / Markdown).

::: dandy.infrastructure.recorder.events.EventType

::: dandy.infrastructure.recorder.events.EventAttribute

::: dandy.infrastructure.recorder.events.Event

::: dandy.infrastructure.recorder.events.EventStore

::: dandy.infrastructure.recorder.recording.Recording

::: dandy.infrastructure.recorder.recorder.Recorder
    options:
        members:
            - add_event
            - start_recording
            - stop_recording
            - stop_all_recording
            - is_recording
            - get_recording
            - delete_recording
            - delete_all_recordings
            - to_html_file
            - to_html_str
            - to_json_file
            - to_json_str
            - to_markdown_file
            - to_markdown_str

::: dandy.infrastructure.recorder.renderer.renderer.BaseRecordingRenderer

::: dandy.infrastructure.recorder.decorators
    options:
        members:
            - recorder_to_html_file
            - recorder_to_json_file
            - recorder_to_markdown_file

::: dandy.infrastructure.recorder.exceptions

## Futures

[Concurrency](../user_guide/futures.md): the thread-pool future and the free function
that runs a callable on the pool.

::: dandy.infrastructure.future.future.AsyncFuture
    options:
        members:
            - cancel
            - cancelled
            - done
            - get_result
            - result
            - set_timeout

::: dandy.infrastructure.future.tools.process_to_future

::: dandy.infrastructure.future.exceptions

# Recording

**Domain concept:** [Event and Recording](../domain_model/glossary.md#glossary) — the
observability context. Behavior captured as typed events, rendered as reports.

**Lives in:** `dandy/infrastructure/recorder/`.

## The default: everything is recorded

`Bot.__init_subclass__` installs a wrapper around `process` at class-creation time, so
every `Bot.process` call auto-records its request, response, retries, and result as
[domain events](../domain_model/tactical.md#domain-events). You do not opt in per call —
the framework's behavior is observable by construction.

```python
from dandy import Recorder

Recorder.start_recording('my_session')
# ... any Bot.process calls ...
Recorder.stop_recording('my_session')

Recorder.to_markdown_file('my_session')   # or to_html_file / to_json_file
```

Renderings write to `{BASE_PATH}/.dandy/recordings/` and require
`ALLOW_RECORDING_TO_FILE = True` in settings.

## Events

An `Event` is one fact: an id, an object name, a callable name, an `EventType`
(`run`, `retry`, `request`, `response`, `result`, `success`, `warning`, `failure`,
`other`), and attributes (key/value pairs; images and audio can ride along as base64).

Emit your own events alongside the framework's:

```python
from dandy import Recorder
from dandy.infrastructure.recorder.events import Event, EventAttribute, EventType
from dandy.infrastructure.recorder.utils import generate_recorder_event_id

Recorder.add_event(
    Event(
        id=generate_recorder_event_id(),
        object_name='OrderService',
        callable_name='checkout',
        type=EventType.OTHER,
        attributes=[EventAttribute(key='Order ID', value='A-1234')],
    )
)
```

## The Recording

A `Recording` is the identity-bearing container of a session: name, start/stop times,
token usage, run time, and the event store. Renderers project it to HTML, JSON, or
Markdown without mutating it. Useful `Recorder` methods:

- `is_recording` — whether a recording is live.
- `get_recording(name)` — the recording object (events included).
- `delete_recording(name)`, `delete_all_recordings()` — cleanup.
- `to_html_str / to_json_str / to_markdown_str` — in-memory renderings.

## Where events come from

The per-subsystem event builders live in the recorder adapter next to the things they
observe: `bot_events.py`, `llm_events.py`, `tool_events.py`, `decoder_events.py`,
`diligence_events.py`. Each is a [documented seam](../architecture/layering.md#documented-seams):
the application emits, the adapter shapes and stores.

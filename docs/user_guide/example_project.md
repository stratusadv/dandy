# Example Project

**Domain concept:** multi-bot orchestration — [Intel](../domain_model/glossary.md#glossary)
flowing between named [Bots](bots.md) until a whole work product exists.

**Lives in:** `tests/application/example_project/book/` in this repository. It is the
framework's own reference for "how to compose many bots", and it follows the
[recommended project structure](../getting_started/project_structure.md) exactly.

## What it does

`create_book(user_input, chapter_count=10)` turns one line of premise into a complete
book: a theme, a title and overview, a cast of characters, a world, a plot, and the
chapters themselves. Every stage is an LLM call returning a validated Intel, and each
stage's Intel feeds the next stage's prompt.

```text
create_book(user_input)
  │  BookThemeDecisionBot ────────────── theme (Decision → enum)
  │  BookStartLlmBot ─────────────────── title + overview
  ├── characters_creation(book_intel) ─── cast (one bot call per character type)
  ├── WorldCreationBot ────────────────── world
  ├── plot_creation(book_intel, n) ────── plot points (outline, then descriptions)
  └── chapters_creation(book_intel, n) ── chapters (plan, then scenes, then content)
→ Book (models.py) — a plain dataclass, serializable to markdown
```

## The accumulator Intel

The stages share one object, `BookIntel` (`intelligence/intel.py`): each stage fills
its own field, and every later prompt is built from the fields filled so far.

```python
class BookIntel(BaseIntel):
    user_input: str
    theme: BookTheme
    start: BookStartIntel | None = None
    characters: CharactersIntel | None = None
    plot: PlotPointsIntel | None = None
    world: WorldIntel | None = None
    chapters: ChaptersIntel | None = None
```

The nested fields are the other packages' intels (`CharactersIntel`,
`PlotPointsIntel`, ...), so each sub-package stays self-contained while the top level
stays one typed object.

## The workflow layer

Orchestration is plain Python — no orchestration class. `workflow.py` at the base of
`intelligence/` threads the accumulator through each stage:

```python
def create_book(user_input: str, chapter_count: int = 10) -> Book:
    book_intel = BookIntel(
        user_input=user_input,
        theme=BookThemeDecisionBot().process(user_input),
    )
    book_intel.start = BookStartLlmBot().process(user_input)
    book_intel.characters = characters_creation(book_intel)
    book_intel.world = WorldCreationBot().process(book_intel)
    book_intel.plot = plot_creation(book_intel=book_intel, chapter_count=chapter_count)
    book_intel.chapters = chapters_creation(book_intel=book_intel, chapter_count=chapter_count)
    ...
```

Each sub-package (`character/`, `world/`, `plot/`, `chapter/`) has its own
`bots/`, `intel.py`, `prompts.py`, and a `workflow.py` with a `*_creation` function.
Two of them show the loop pattern — a planning pass, then one bot call per item:

- `plot_creation`: `PlotOutlineBot` returns the plot points, then
  `PlotPointDescriptionBot` rewrites each one, receiving the already-written points so
  the descriptions stay consistent.
- `chapters_creation`: `ChaptersLlmBot` plans the chapters, then for each chapter
  `SceneLlmBot` plans its scenes and `ChapterContentLlmBot` writes the prose — each
  pass updating the same `ChaptersIntel` in place.

## The pieces worth stealing

- **A Decision as the first call** (`intelligence/decisions.py`):
  `BookThemeDecisionBot.process` runs `self.llm.decision.prompt_to_value` over a
  `keys_values` map and returns a `BookTheme` enum member — the whole book is then
  themed from a bounded, validated choice instead of free text.
- **Bots that take an Intel, not a string** (`world/bots.py`):
  `WorldCreationBot.process(book_intel)` builds its prompt from the accumulator
  (`title`, `overview`, characters) with `Prompt` — the bot's input is the domain
  object, string-building stays inside the bot.
- **Prompt builders shared across bots**: `character/prompts.py` exports
  `characters_intel_prompt`, reused by `WorldCreationBot` — prompts live in
  `prompts.py` and are functions, so composition is import-and-call.
- **`logging.info` at every stage**: a long pipeline is debuggable when each hand-off
  announces itself; run it under the [Recorder](recording.md) and the full event
  trail is one HTML file away.

## Running it

The example is exercised by a live-LLM test —
`tests/application/example_project/test_example_project.py`
(`@live_llm_test`, two chapters, recorded to HTML). It skips in the hermetic suite;
with a real `AI_API_KEY` it runs in the `optional-testing` CI job (about 110 seconds):

```bash
DANDY_SETTINGS_MODULE=tests.dandy_settings python -m pytest \
  tests/application/example_project/test_example_project.py -v
```

The assertions are deliberately about the *shape* of the result — a `Book` with a
non-empty title, overview, and two non-empty chapters — not about the prose.

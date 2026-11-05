# Project Structure

Working with intelligence means keeping two scopes in your head at once — your domain
code and the AI interactions it drives. As the AI surface grows, an unorganized
project becomes hard to reason about. This is the recommended layout for user code
built on Dandy; the framework's own five-layer structure
([Layering](../architecture/layering.md)) binds `dandy/` itself, not your project.

The rule of thumb: **all Dandy-related code lives in an `intelligence/` directory**
beside the code it serves. Your models, services, and business logic stay where they
already are.

!!! tip

    The [Example Project](../user_guide/example_project.md) in this repo follows this
    structure exactly, and the framework's own test suite keeps its fixtures under
    `intelligence/` directories for the same reason.

## Basic structure

For a module with a little AI in it, a few files inside `intelligence/` are enough:

``` title="Basic project structure"
📁 book/                    <-- your module
 ├── 📄 __init__.py
 ├── 📄 models.py
 ├── 📄 your_code.py
 └── 📁 intelligence/       <-- all Dandy-related code lives here
      ├── 📄 __init__.py
      ├── 📄 bots.py
      ├── 📄 intel.py
      └── 📄 prompts.py
📄 __init__.py
📄 dandy_settings.py
📄 main.py
```

## Advanced structure

When a module has several distinct AI tasks, give each one its own package under
`intelligence/`, and give each bot its own file:

``` title="Advanced project structure"
📁 book/
 ├── 📄 __init__.py
 ├── 📄 models.py
 ├── 📄 your_code.py
 └── 📁 intelligence/
      ├── 📁 bots/
      │    ├── 📄 __init__.py
      │    └── 📄 book_start_bot.py    <-- one bot per file (its intels and
      │                                    prompts may live in the same file)
      ├── 📁 chapter/
      │    ├── 📁 bots/
      │    │    ├── 📄 __init__.py
      │    │    ├── 📄 chapters_planning_bot.py
      │    │    ├── 📄 scene_bot.py
      │    │    └── 📄 chapter_content_bot.py
      │    ├── 📄 __init__.py
      │    ├── 📄 intel.py             <-- Intel classes, always suffixed "Intel"
      │    ├── 📄 prompts.py
      │    └── 📄 workflow.py
      ├── 📁 character/
      │    ├── 📁 bots/
      │    │    ├── 📄 __init__.py
      │    │    └── 📄 character_description_bot.py
      │    ├── 📄 __init__.py
      │    ├── 📄 enums.py             <-- related code beside its intels keeps
      │    │                                concerns separated
      │    ├── 📄 intel.py
      │    ├── 📄 prompts.py
      │    └── 📄 workflow.py
      ├── 📄 __init__.py
      ├── 📄 intel.py
      └── 📄 workflow.py              <-- multi-step orchestration for the whole
                                          module sits at the base of intelligence/
📄 __init__.py
📄 dandy_settings.py        <-- settings and LLM configs for the whole project
📄 main.py                  <-- entry point
```

## The conventions

- **`intelligence/` per module.** Every Dandy import — bots, intels, prompts,
  decisions, workflow orchestration — goes in this directory. Business code imports
  *from* `intelligence/`, never the other way around.
- **One bot per file** in `bots/`, named after the bot: `scene_bot.py` holds
  `SceneLlmBot`. A file may also hold the Intel and prompt builders that bot
  exclusively uses; shared ones go in the package's `intel.py` / `prompts.py`.
- **Intel classes are suffixed `Intel`** (`BookStartIntel`, `ChaptersIntel`). The
  suffix makes the domain contract visible at a glance and keeps it distinct from
  your regular models.
- **`intel.py` / `prompts.py` / `workflow.py`** are the standard package files: the
  typed answers, the prompt builders, and the multi-step orchestration that threads
  the intels between bots ([see the Example Project](../user_guide/example_project.md)
  for `workflow.py` in action).
- **`dandy_settings.py` at the project root** holds `BASE_PATH` and `LLM_CONFIGS`
  for the whole project — see [Configuration](configuration.md).

!!! note

    Inside your own project, import the public API from the `dandy` root
    (`from dandy import Bot, BaseIntel, Prompt`) — the layering rules and their
    import restrictions apply to the framework package, not to your code.

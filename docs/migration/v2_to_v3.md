# Migrating from 2.x to 3.0

!!! warning "Breaking release"
    3.0.0 is a breaking release. Every module moved to a new import path as part of the
    physical [domain-driven restructure](../architecture/layering.md). Behavior, the
    public API, and configuration semantics are unchanged; import paths are not.

## What changed, what didn't

**Changed:** the internal package layout. The flat 2.x layout
(`dandy/bot`, `dandy/llm`, `dandy/intel`, `dandy/core`, ...) is now a four-layer
structure plus a shared kernel: `dandy/domain`, `dandy/application`,
`dandy/infrastructure`, `dandy/interfaces`, `dandy/shared`. Any code that imports from
inside the framework (anything other than the package root) must update its imports.

**Unchanged:**

- The **public API**. Everything re-exported from the `dandy` root still exists and
  still works: `Bot`, `Prompt`, `BaseIntel`, `BaseListIntel`, `BaseTool`, `Recorder`,
  `MemoryCache`, `SqliteCache`, `cache_to_memory`, `cache_to_sqlite`,
  `generate_cache_key`, `process_to_future`, `recorder_to_html_file`,
  `recorder_to_json_file`, `recorder_to_markdown_file`, and the exceptions
  `DandyError`, `DandyCriticalError`, `DandyRecoverableError`.
- **Configuration.** `DANDY_SETTINGS_MODULE`, the `dandy_settings.py` module, the
  `dandy.json` fallback, `LLM_CONFIGS` with a required `DEFAULT` entry, `CLI_CONFIG`
  task mapping, and `CONTEXT_SIZE` all work exactly as before.
- **Behavior.** Prompt building, Intel validation and retries, the tool loop, decoder
  retries, the reset chain, recording, caching, futures, and the CLI are unchanged.
  The OpenAI-compatible-endpoint contract is unchanged.
- **Tests.** The suite is the same suite, reorganized to mirror the new layout.

## Old to new package map

| 2.x import path | 3.0 import path |
|---|---|
| `dandy.intel.intel` (BaseIntel, BaseListIntel, DefaultIntel) | `dandy.domain.intel.intel` |
| `dandy.intel.factory` (IntelFactory) | `dandy.domain.intel.factory` |
| `dandy.intel.service` (IntelService) | `dandy.domain.intel.service` |
| `dandy.intel.typing`, `dandy.intel.field.annotation` | `dandy.domain.intel.typing`, `dandy.domain.intel.field.annotation` |
| `dandy.intel.exceptions` | `dandy.domain.intel.exceptions` |
| `dandy.tool.tool` (BaseTool, run_subprocess) | `dandy.domain.tool.tool` |
| `dandy.tool.exceptions` | `dandy.domain.tool.exceptions` |
| `dandy.llm.prompt.*` (Prompt, snippets) | `dandy.domain.llm.prompt.*` |
| `dandy.llm.request.*` (Message, MessageHistory, LlmRequestBody) | `dandy.domain.llm.request.*` |
| `dandy.llm.options` (LlmOptions) | `dandy.domain.llm.options` |
| `dandy.llm.tokens` (token estimation) | `dandy.domain.llm.tokens` |
| `dandy.llm.exceptions` | `dandy.domain.llm.exceptions` |
| `dandy.llm.tool.intel` (LlmToolCall(s)Intel) | `dandy.domain.llm.tool.intel` |
| `dandy.llm.decoder.intel`, `dandy.llm.decoder.exceptions` | `dandy.domain.llm.decoder.*` |
| `dandy.llm.intelligence.prompts`, `dandy.llm.decoder.intelligence.prompts` | `dandy.domain.llm.intelligence.prompts`, `dandy.domain.llm.decoder.intelligence.prompts` |
| `dandy.bot.*` (Bot) | `dandy.application.bot.*` |
| `dandy.llm.service`, `dandy.llm.mixin` | `dandy.application.llm.service`, `dandy.application.llm.mixin` |
| `dandy.llm.tool.service`, `dandy.llm.tool.mixin` | `dandy.application.llm.tool.service`, `dandy.application.llm.tool.mixin` |
| `dandy.llm.decoder.decoder`, `.../service`, `.../mixin` | `dandy.application.llm.decoder.decoder`, `.../service`, `.../mixin` |
| `dandy.llm.diligence.*` | `dandy.application.llm.diligence.*` |
| `dandy.cli.intelligence.*` (CodingAgent, bots, prompts) | `dandy.application.agent.*` |
| `dandy.cli.intelligence.tools.*` (agent tools) | `dandy.application.agent.tools.*` |
| `dandy.cli.session` | `dandy.application.agent.session` |
| `dandy.llm.connector`, `dandy.llm.config` | `dandy.infrastructure.llm.connector`, `dandy.infrastructure.llm.config` |
| `dandy.http.*` | `dandy.infrastructure.http.*` |
| `dandy.file.service`, `dandy.file.mixin` | `dandy.infrastructure.file.service`, `dandy.infrastructure.file.mixin` |
| `dandy.file.utils`, `dandy.file.exceptions` | *removed* (file helpers moved to `dandy.shared.files`) |
| `dandy.file.audio.*`, `dandy.file.image.*` | *removed* (moved to `dandy.shared.media`) |
| `dandy.cache.*` | `dandy.infrastructure.cache.*` |
| `dandy.recorder.*` | `dandy.infrastructure.recorder.*` |
| `dandy.core.future.*` | `dandy.infrastructure.future.*` |
| `dandy.core.service.*` | `dandy.shared.service.*` |
| `dandy.core.connector.*` | `dandy.shared.connector.*` |
| `dandy.core.typing.*` | `dandy.shared.typing.*` |
| `dandy.core.exceptions` | `dandy.shared.exceptions` |
| `dandy.core.singleton` | `dandy.shared.singleton` |
| `dandy.core.utils` | `dandy.shared.utils` |
| `dandy.core.debug` | `dandy.shared.debug` |
| `dandy.core.constants` | `dandy.shared.constants` |
| `dandy.constants` | `dandy.shared.constants` |
| `dandy.conf.*` | `dandy.shared.conf.*` |
| `dandy.default_settings` | `dandy.shared.conf.default_settings` |
| `dandy.cli.*` (REPL, TUI, main) | `dandy.interfaces.cli.*` |

## How to migrate

1. **Move to root imports wherever possible.** If your code only uses the public API,
   replace `from dandy.<module> import X` with `from dandy import X`. That is the
   stable contract and it will not move again.
2. **For internal imports, apply the map.** A few `sed` passes over the table above
   cover most codebases:
   ```bash
   sed -i \
       -e 's/from dandy\.intel\./from dandy.domain.intel./g' \
       -e 's/from dandy\.tool\./from dandy.domain.tool./g' \
       -e 's/from dandy\.llm\.prompt\./from dandy.domain.llm.prompt./g' \
       -e 's/from dandy\.llm\.request\./from dandy.domain.llm.request./g' \
       -e 's/from dandy\.llm\.options import/from dandy.domain.llm.options import/g' \
       -e 's/from dandy\.bot\./from dandy.application.bot./g' \
       -e 's/from dandy\.llm\.decoder\./from dandy.application.llm.decoder./g' \
       -e 's/from dandy\.llm\.diligence\./from dandy.application.llm.diligence./g' \
       -e 's/from dandy\.llm\.tool\./from dandy.application.llm.tool./g' \
       -e 's/from dandy\.llm\.service import/from dandy.application.llm.service import/g' \
       -e 's/from dandy\.llm\.mixin import/from dandy.application.llm.mixin import/g' \
       -e 's/from dandy\.llm\.connector import/from dandy.infrastructure.llm.connector import/g' \
       -e 's/from dandy\.llm\.config import/from dandy.infrastructure.llm.config import/g' \
       -e 's/from dandy\.http\./from dandy.infrastructure.http./g' \
       -e 's/from dandy\.file\./from dandy.infrastructure.file./g' \
       -e 's/from dandy\.cache\./from dandy.infrastructure.cache./g' \
       -e 's/from dandy\.recorder\./from dandy.infrastructure.recorder./g' \
       -e 's/from dandy\.core\.future\./from dandy.infrastructure.future./g' \
       -e 's/from dandy\.core\.service\./from dandy.shared.service./g' \
       -e 's/from dandy\.core\.connector\./from dandy.shared.connector./g' \
       -e 's/from dandy\.core\.typing\./from dandy.shared.typing./g' \
       -e 's/from dandy\.core\.\(exceptions\|singleton\|utils\|debug\) import/from dandy.shared.\1 import/g' \
       -e 's/from dandy\.constants import/from dandy.shared.constants import/g' \
       -e 's/from dandy\.conf\./from dandy.shared.conf./g' \
       -e 's/from dandy import default_settings/from dandy.shared.conf import default_settings/g' \
       $(git grep -l 'from dandy\.' -- '*.py')
   ```
   Then fix the few remaining cases by hand (the table is authoritative).
3. **Verify.** Run your test suite. If you contribute back to this repo, also run
   `just lint-imports` and `just test`.

## The architecture contracts (for contributors)

3.0 enforces the layering with [import-linter](https://github.com/seddonym/import-linter)
in CI (`just lint-imports`). Six contracts run:

1. Domain layer must not import outer layers
2. Shared kernel must not import any layer
3. Application layer must not import interface layer
4. Infrastructure layer must not import application or interface layers
5. Application layer imports infrastructure only at documented seams
6. Interface layer imports infrastructure only at documented seams

Contracts 5 and 6 are allow-list contracts: the specific
application-to-infrastructure and interface-to-infrastructure edges that are necessary
(the services building their connectors, the CLI loading its settings) are listed
explicitly in `pyproject.toml`, and any other cross-layer import fails the build. If
you need a new edge, the correct move is almost always to route the dependency through
a domain object or a shared-kernel seam instead. See
[Layering and Dependency Rules](../architecture/layering.md) for the full discussion.

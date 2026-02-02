# Changelog

## v2.0.0.alpha

### Major Release

- This is a major release, and we highly recommend reading our documentation before upgrading.

### Breaking

- Ollama API support has been removed from this project and is now defaulted to the OpenAI API standard.
- Since Ollama supports the OpenAI API standard, you can continue to use Dandy with Ollama.
- Removed `calculator` module.
- Removed `processor` module and `BaseProcessor` class; `Bot` is now the primary entry point.
- Adapted `Decoder` from standalone processor into a service usable via the `Bot` module.
  - `Bot().llm.decoder`
- Removed `Agent` module.
- Removed all `LLM_DEFAULT_*` from settings and now require it to be set inside of `LLM_CONFIGS` for each model.
  - By default, it uses the defaults on the llm endpoint.
- All exceptions that were postfixed `Exception` are now postfixed `Error`.
  - Example: `DandyCriticalException` is now `DandyCriticalError`
- The example project has been removed.
- Removed `PromptOrStr` and `PromptOrStrOrNone` TypeAlias's.
- Removed `toolbox` module (functionality replaced by the new CLI).
- Removed `makefile`.
- All `Prompt` methods have had the argument `triple_quote` changed to `triple_backtick`.

### Changes

- All options in `LLM_CONFIGS` now need to be inside an `OPTIONS` key and are set as lower case keys.
  - Example: `OPTIONS: {'temperature': 1.4, 'top_p': 0.7, 'frequency_penalty': 0.2, 'presence_penalty': 0.1}`.

### Features

- `FileService` is now available on `Bot` via `Bot().file` to make it easy to manipulate and work with files.
- `HttpService` is now available on `Bot` via `Bot().http` for making HTTP requests.
- `IntelService` is now available on `Bot` via `Bot().intel` for manipulating `Intel` classes and objects.
- The `Bot().llm.prompt_to_intel` method now supports Vision and Audio.
- The command line interface is back and better than ever, check it out by typing `dandy` in your terminal.
  - Type into the input to learn more about the features.
  - Use `/` to run a command.
- `BaseListIntel` is a new base class for creating Intel objects that primarily wrap a list of items, providing list-like access.
- `DefaultIntel` is a simple Intel class with a `text` field for quick use.
- The `BaseIntel` has some new convenience methods `save_to_file` and `create_from_file` for easy long-term storage.
- Configuring LLM options can now be done through `Bot().llm.options` and `Bot().llm.decoder.options`.
  - Example: `new_bot = Bot() ... new_bot.llm.options.temperature=1.4`

### Fixes

- Fixed a bug with `directory_list` method on the `Prompt` class when a file has no extension.
- `dandy.llm.conf.LlmConfigs` are now checked during usage to allow for better control loading environments.
- `dandy.conf.settings` now reloads its current state at the time of attribute access instead of once during init.
- Fixed many issues with customizing all `Service` and `Processor` subclasses.
- Decouple a lot of the LLM modules to allow for better maintainability and testing by using the new `LlmConnector`.
- Added `2026_roadmap.md` to track future development plans.
- Reorganized project structure to be more service-oriented.


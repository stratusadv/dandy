# Changelog

## v2.0.0

### Major Release

- This is a major release, and we highly recommend reading our documentation before upgrading.

### Breaking

- Ollama API support has been removed from this project and is now defaulted to the OpenAI API standard.
- Since Ollama supports the OpenAI API standard, you can continue to use Dandy with Ollama.

### Changes

- The `LLM_DEFAULT_MAX_INPUT_TOKENS` and `LLM_DEFAULT_MAX_OUTPUT_TOKENS` have been defaulted to `None`
- The `LLM_DEFAULT_TEMPERATURE` and `LLM_DEFAULT_SEED` have also been defaulted to `None`
- The `LLM_DEFAULT_MAX_INPUT_TOKENS` and `LLM_DEFAULT_MAX_OUTPUT_TOKENS` have been replaced with `LLM_DEFAULT_MAX_COMPLETION_TOKENS` to match with the api changes.

### Features

- `FileService` is now available on `Bot` to make it easy to manipulate and work with files.
- The command line interface is back and better than ever, check it out by typing `dandy` in your terminal.
  - Type into the input to learn more about the features.
  - Use `/` to run a command.
- The `BaseIntel` has some new convenience methods `save_to_file` and `create_from_file` for easy long-term storage.
- New `VisionService` has been added to bots.
  - ********* put more information about the vision service here ***********
- New `AudioService` has been added to bots.
  - ********* put more information about the vision service here ***********

### Fixes

- Fixed a bug with `directory_list` method on the `Prompt` class when a file has no extension.
- `dandy.llm.conf.LlmConfigs` are now checked during usage to allow for better control loading environments.
- `dandy.conf.settings` now reloads its current state at the time of attribute access instead of once during init.
- Fixed many issues with customizing all `Service` and `Processor` subclasses.
- Decouple a lot of the llm modules to allow for better maintainability and testing.


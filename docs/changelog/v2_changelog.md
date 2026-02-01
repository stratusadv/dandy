# Changelog

## v2.0.0

### Major Release

- This is a major release, and we highly recommend reading our documentation before upgrading.

### Breaking

- Ollama API support has been removed from this project and is now defaulted to the OpenAI API standard.
- Since Ollama supports the OpenAI API standard, you can continue to use Dandy with Ollama.
- Removed `calculator` module.
- Adapted `Decoder` from standalone processor into a service usable via the `Bot` module.
  - `Bot().llm.decoder`
- Removed `Agent` module.
- Removed all `LLM_DEFAULT_*` from settings and now require it to be set inside of `LLM_CONFIGS` for each model.
  - By default, it uses the defaults on the llm endpoint.
- All exceptions that were postfixed `yException` are now postfixed `Error`.
  - Example: `DandyCriticalException` is now `DandyCriticalError`
- The example project has been removed.

### Changes

- All options in `LLM_CONFIGS` now need to be inside an `OPTIONS` key and are set as lower case keys.
  - Example: `OPTIONS: {'temperature': 1.4, 'top_p': 0.7, 'frequency_penalty': 0.2, 'presence_penalty': 0.1}`.

### Features

- `FileService` is now available on `Bot` to make it easy to manipulate and work with files.
- The `Bot().llm.prompt_to_intel` method now supports Vision.
- The command line interface is back and better than ever, check it out by typing `dandy` in your terminal.
  - Type into the input to learn more about the features.
  - Use `/` to run a command.
- The `BaseIntel` has some new convenience methods `save_to_file` and `create_from_file` for easy long-term storage.

### Fixes

- Fixed a bug with `directory_list` method on the `Prompt` class when a file has no extension.
- `dandy.llm.conf.LlmConfigs` are now checked during usage to allow for better control loading environments.
- `dandy.conf.settings` now reloads its current state at the time of attribute access instead of once during init.
- Fixed many issues with customizing all `Service` and `Processor` subclasses.
- Decouple a lot of the llm modules to allow for better maintainability and testing.


# Changelog

## v0.15.0

### Features

- The `Recorder` module now properly tracks token usage and run times.

### Changes

- Move around and update elements in the html rendered output for the `Recorder` class.

### Fixes

- Updated `Recording` class to properly track token usage and run times.
- Removed the broken `assistant_str_prompt_to_str` method from `BaseLlmConfig` and `LlmService` classes.

## v0.14.6

### Fixes

- Rename `EventItem` to `EventAttribute` for more seperation of concerns when it comes to dictionaries.

## v0.14.5

### Fixes

- Fixed a problem with the `Recorder` class not outputting strings.

## v0.14.4

### Breaking

- All of the `recorder` decorators have been renamed to `recorder_to_html_file`, `recorder_to_markdown_file` and `recorder_to_json_file`.

### Fixes

- Remove relative path system from dandy as it caused to many edge case problems.

## v0.14.3

### Fixes

- Fixed a problem with `SqliteCache` not handling cleared tables correctly.
  - Added the `clear_all` method to `MemoryCache` and `SqliteCache` to fix clearing caches properly.
- Fixed recorder shortcut methods for rendering to files and strings.

## v0.14.2

### Fixes

- Fixed the `file` method on the `Prompt` to properly hand relative paths.
  - The `relative_parents` argument makes it quick to traverse parent directories by count.

## v0.14.1

### Features

- Added `object_source` method to `Prompt` to get the source of a specific object in a module.
- Drastically improved the LLM service to retry and handle prompt correction.

### Fixes

- Fixed the `dandy.utils` to correct a circular import problem.
- Fixed a problem with the `file` method on the `Prompt` class to search the `settings.BASE_PATH` directory.

## v0.14.0

### Breaking

- The `debug` module is now the `recorder` module.
  - This also includes many refactors like `DebugRecorder` to `Recorder` ETC.
- In settings `ALLOW_DEBUG_RECORDING` has been removed.
- In settings `ALLOW_RECORDING_TO_FILE` hase been added with a default value of `False`.
- The `destroy` method on `Cache` object has now been replaced with `destroy_all` for clearing all caches.

### Features

- `DebugRecorder` is now `Recorder` and has new rendering methods and overall improved rendering quality.
  - You can now render to json, html and markdown files and strings for easy exporting.

### Changes

- `SqliteCache` now uses one file to store all different caches.
  - this allows for more fine control in the same way the `MemoryCache` works.

### Fixes

- Fixed the llm service to properly handle retrying when an invalid response is provided with progressive exceptions.
- Improved the `BaseIntel` class to have much better handling for complex operations.

## v0.13.3

### Breaking

- Moved 'dandy.core.cache' to 'dandy.cache'

### Fixes

- Debug recorder correctly renders OpenAI service request messages.
- Added more testing for more complex JSON Schemas.
- Fixed a bug where the `Prompt.prompt` method would not accept strings properly.

## v0.13.2

### Fixes

- Fixed problem with `BaseIntel` required fields using nested includes and excludes.

## v0.13.1

### Fixes

- Fixed bug with using include and exclude on `BaseIntel` objects that did not validate filled and empty fields properly.

## v0.13.0

### Breaking

- Removed the `assistant_str_prompt_to_str` method and sub methods from `LlmService`.
  - Everything should be processed through the `LlmBot` going forward.

### Features

- Added a new processor called `LlmMap` that uses the `Map` object to easily create contextual relationships to python objects.
- Debug recorder now shows the JSON schema that was sent to the llm service.
- New decorator called `debug_recorder_to_html(debug_name: str)` that allows you to easily wrap a function or method.

### Changes

- Removed the Contrib Selection llm bot.

### Fixes

- Fixed a caching to be more robust and understand changes with in dandy processors for more accurate caching.
- Drastically improved the testing of the OpenAI llm service.

## v0.12.0

### Features

- The `BaseLlmBot` now supports `images` and `image_files` in the `process_prompt_to_intel` method.
  - Make sure you have the `config` using a compatible llm model that supports vision.

### Fixes

- Fixed the hash key generation process to work with more data types and maintain better consistency.
- Improved testing of the OpenAI llm service.

## v0.11.3

### Changes

- Refactored internal project structure to get ready for next AI features (TTS, STT, VISION ETC).

### Fixes

- Fixed a bug with clearing non-existent or empty caches.

## v0.11.2

### Notes

- This release was combined with v0.11.1 for a single release.

### Features

- Updated example with better use of `Prompt` objects.
- Added `to_markdown_file` method for the `Book` class in the example.
- Updated caching objects to be easier to clear.
  - `dandy.cache.MemoryCache` and `dandy.cache.SqliteCache` have class method `clear` and `destroy`.

### Fixes

- Added text to global service prompt to improve response quality.
- Fix bug with updating non-flat intel objects.

## v0.11.0

### Breaking

- All uses of the `process_prompt_to_intel` method now require you to specify either an `intel_class` or an `intel_object` argument.

### Features

- A new example has been created that is much easier to follow and showcases the features of Dandy.
- Added a new `Intel` class called `BaseListIntel` that is used to create an iterable intel object that behaves like a `list`.
- When using `process_prompt_to_intel` you can now submit a `intel_class` or `intel_object`.
  - Submitting a class will return you a new instance of the class.
  - Submitting the object will return you a modified copy of the object.
- The method `process_prompt_to_intel` now supports `include_fields` and `exclude_fields` which allow you to only include or exclude fields from the intel object or class.
- Caching is now supported through the `cache_to_memory` and `cache_to_sqlite` decorators.
  - Check out the `dandy/default_settings.py` file to see how to configure caching beyond the defaults.
  - Decorator argument `cache_name` which can be used to separate the cache objects / files, default is `dandy`.
  - Decorator argument `limit` which can be used to set an upper limit on the number of items that can be cached, default is in `settings`.

### Changes

- Removed the old examples (Cookie Recipe and Pirate Story)
- Exceptions are now being divided into two categories: `DandyCriticalException` and `DandyRecoverableException`.
  - Both of this will inherit from `DandyException`.
  - The `DandyRecoverableException` will be used to allow developers to attempt recovering from exceptions safely.
  - The `DandyCriticalException` will be for when an exception is unrecoverable and must be handled.

### Fixes

- Update the `process_to_intel` method used throughout the project to properly reflect the `postfix_system_prompt` argument.
- Added missing return to the `__str__` method in the `Url` class (Thanks Pyright).

## v0.10.0

### Breaking

- Renamed `Bot` to `BaseBot`
- Renamed `Workflow` to `BaseWorkflow`
- The LLM API for Ollama now only works with 0.5.0 or greater.
- The LLM API for OpenAI now only works with gpt-4o-mini or greater.

### Documentation

- We have an initial working documentation website that can be viewed at https://dandysoftware.com
- Our new website is powered by mkdocs, mkdocstrings, mkdocs-include-markdown-plugin and mkdocs-material.

### Features

- In the `LLM_CONFIGS` in your settings the `TYPE`, `HOST`, `PORT` AND `API_KEY` from the `DEFAULT` config will now flow to the other configs if they are not specificed.
- Added --version to the CLI interface for Dandy.
- The OpenAI llm service now use json_schema for the response format.
- The OllamaAI llm service now use json_schema for the response format.

### Changes

- Rebuilt the document structure.

### Fixes

- Dandy CLI now properly create default settings based on your environment variables.
- Fixed the way the settings are handled so they properly show error messages for missing settings.

## v0.9.2

### Fixes

- Update requirements.txt

## v0.9.1

### Fixes

- Added default instructions prompt to the `LlmBot` class.

## v0.9.0

### Features

- LlmBots now have a default built in process method that takes in a prompt and returns an intel object.
- Changed our http handling library to httpx.
- The contrib choice llm bot has been replaced with the much simpler selector llm bot.
- The Prompt class init now has a text argument that will create a prompt with a text snippet automatically for simple prompts.
- New setting `DEFAULT_LLM_REQUEST_TIME_OUT` that controls the timeout for LLM requests default is `None`.

### Changes

- Moved `llm_bot` from `dandy.bot` to `dandy.llm.bot` to match our refactoring changes.
- Changed the base class from `Handler` to `BaseProcessor`
- Refactored `Intel` to `BaseIntel` to improve readability.
- Added `BaseLlmBot` class to `dandy.llm.bot` to be used for creating all llm bots.
- `BaseLlmBot` config now takes just a string that is one of the `LLM_CONFIGS` in the settings.

### Fixes

- There is now a `DefaultLlmIntel` class that is used as the default intel class for LlmBots that has one attribute called `text`.
- Fixed a bunch of Generic Type handling through-out the project.
- Connection retry count of zero no longer causes an error.
- Refactor llm internal packages to match their usage better.
- Fixed AsyncFuture to allow you to access the result after accessing it once.
- Fixed CLI to properly load environment variables and settings in the correct order.

## v0.8.1

### Fixes

- Fixed the settings module validation to be much easier to implement and debug.
- Fixed but that accidentally overwrote settings files for the user.

## v0.8.0

### Major Changes

- We have created a new class called `Intel` that is the pydantic `BaseModel` class renamed to give more separation of concerns between Dandy code and your code.
- For the most part of this project the word `Model` has been refactored to `Intel` to create more separation of concerns in projects.
- The word `Model` has a lot of meaning in the context of Dandy, artificial intelligence, databases, libraries and other frameworks.
- Our hope is this creates a very clear line between these specific objects and the rest of your code.

## v0.7.0

### Major Improvement

- All the changes in v0.7.0 should reduce the over all code required to work with Dandy by up to 50%.

### Features

- Project structure improvement with new settings file.
- All projects going forward will require a `dandy_settings.py` file in the root of your project.
  - This file will also need a `BASE_PATH` str variable set to the root of your project.
  - This file will also need a `LLM_CONFIGS` dict variable with a `DEFAULT` llm config.
- Debug recorder can now output to a json string or file.
- Added randomize seed to LLM config that will randomize the seed every time the config is used.
- Added new evaluate cli command for evaluating your Dandy code -e --evaluate.
  - Currently only supports Prompt evaluation.
- ALLOW_DEBUG_RECORDING was added to the settings for project wide control of the debug recorder.
  - defaulted to False.
- You can now select your llm config from the cli using the -l --llm-config flag.

### Changes

- Updated the readme to match the new project structure.
- All settings and llm configs are now managed through the Dandy settings module.
  - The environment variable `DANDY_SETTINGS_MODULE` can be used to specify the settings module to be used.
  - The system will default to look for a `dandy_settings.py` file in the current working directory or sys.path.
- Moved a lot of project wide constants into the `const.py` file.

### Fixes

- Fixed the user `dandy_settings.py` not loading properly with in the internal Dandy modules.
- Fixed readme to match new project structure and configuration setup.
- Fixed the cli to properly use the dandy_settings.py file in the current working directory.
- Improved testing coverage across the whole project.


# Archived Changelog

## v0.20.0

### Features

- LLM Agents
  - Dandy now supports agentic processing through the `LlmAgent` module located in `dandy.llm`.
  - Works very similarly to a `LlmBot` but requires `processors` attribute that is a sequence of `BaseProcessor` subclasses.
  - All `processors` must have a `description` attribute to tell the agent how to use them and when.

### Fixes

- Fixed a bug on `LlmBot` that prevented you from using the `intel_object` argument in the `process` method.
- `BaseProcessor` method `process` now maintains it's signature properly.

## v0.18.0

### Breaking

- `BaseListIntel` now works by creating a single attribute in the subclass that must be typed as a list.

### Features

- The `BaseLlmMap` class now has a new required attribute `map_keys_description` that drastically improves accuracy.

### Changes

- On the `BaseLlmMap.process` the argument `choice_count` was renamed to `max_return_values` to make it more clear what it does and is now optional.
- The `BaseListIntel` now requires you to set the type of the `items` class variable with a type hint.

### Fixes

- Changed `Prompt` into a dataclass to allow typing with `BaseIntel`, `BaseListIntel` and `BaseModel`.
- Fixed a problem with the way `BaseLlmMap` was prompting for single responses using `max_return_values=1`.
- `LlmService` has been refactored to handle retrying and progressive exceptions much better.

## v0.17.0

### Features

- Added a new `calculator` module to dandy to help solve math problems related to using `Dandy`.
  - In `dandy.calculator.llm_calculator` you can find `model_size_for_inference_to_vram_gb` and `model_size_and_token_count_for_inference_to_vram_gb`
- There is a quick shortcut in the dandy cli to `model_size_and_token_count_for_inference_to_vram_gb` using the -c flag.

## v0.16.0

### Features

- Added a new `MessageHistory` class that can be used to submit a history of messages to be used in the request prompt.

### Fixes

- Corrected the `RequestMessage` to have a `Literal['user', 'assistant', 'system']` type for the `role` field.
- Fixed the formatting internally for messages inside the `LlmService` class.

## v0.15.0

### Features

- The `Recorder` module now properly tracks token usage and run times.
- New `delete_all_recordings` and `delete_recording` methods added to the `Recorder` class for memory management.
- New `get_recording` method added to the `Recorder` class for easy access.

### Changes

- Move around and update elements in the html rendered output for the `Recorder` class.

### Fixes

- Updated `Recording` class to properly track token usage and run times.
- Removed the broken `assistant_str_prompt_to_str` method from `BaseLlmConfig` and `LlmService` classes.

## v0.14.6

### Fixes

- Rename `EventItem` to `EventAttribute` for more separation of concerns when it comes to dictionaries.

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

- In the `LLM_CONFIGS` in your settings the `TYPE`, `HOST`, `PORT` AND `API_KEY` from the `DEFAULT` config will now flow to the other configs if they are not specified.
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

## v0.6.1

### Features

- Added heading and sub headings to the prompt class.

### Changes

- Improved testing across the whole project.
- Prompt assembly is more reliable and consistent if you want empty lines you need to use the .line_break method.

### Fixes

- Fixed lots of prompt formatting issues.
- Futures properly raise an exception when they time out.

## v0.6.0

### Features

- You can now cancel futures using the cancel method.
- LLmBots can now be configured with max_input_tokens and max_output_tokens

### Changes

- Removed the role attribute from the llm bot class.
- Updated the readme to match the new project structure.
- Example changed to use more features and provide a better example of usage.
- Refactored a lot of naming to be more clear and direct.

### Fixes

- Fixed futures to properly use the thread pool executor to wait for results.
- Fixed the examples to properly match the new project structure.
- Fixed bug with futures not timing out properly.

## v0.5.2

### Fixes

- Fixed the bearer token usage for use with ollama and reverse proxy servers.

## v0.5.0

### Features

- Improved the debug recorder html output to be more user friendly and easier to read.
- Added ID's to all the tracked events in the debug recorder.

### Changes

- Changed the service controls for ollama to match the new format structure in the request json.

### Fixes

- Fixed the work flow process return display in the debug recorder.
- Fixed all the process control displays in the debug recorder to display properly.

## v0.4.2

### Features

- You can now run simple assistant prompts with the -t --test argument for the Dandy cli.
  - Example: dandy -t `some.module.cool_llm_bot.CoolLlmBot`

## v0.4.1

### Features

- You can now run simple assistant prompts with the -a --assistant argument for the Dandy cli.
  - Example: dandy -a `Hello, how are you?`

## v0.4.0

### Features

- Added a Dandy command line interface.
  - you can use the -g --generate flag to generate a new llm bots.
  - you can use the -d --description flag to describe the llm bot you want to generate.
  - more generation features coming in the future 
- Prompts now have support for module source and files.

### Changes

- Change the method behavior for services to have more options when prompting

### Fixes

- Corrected incorrectly named snippets being used in the prompt. 

## v0.3.1

### Fixes

- Fixed the debug recorder when no events are recorded.
- Changed the debug recorder exception types to DandyException.

## v0.3.0

### Features

- Ollama config now supports max_completion_tokens (num_predict on ollama api) and context_length (num_ctx on ollama api)
- Openai config now supports max_completion_tokens

### Changes

- Single Choice LLM Bots now return only the value when the choices are from a dictionary.
- Multiple Choice LLM Bots now return a list of only the values when the choices are from a dictionary.

### Fixes

- Improved validation on llm configs.

## v0.2.0

### Features

- Added support for async using the thread pool executor to create a future were you can process things into futures.
- use the future.result to get the result of the future.
- Added datetime to the debug recorder output.

### Changes

- Handler, Bots, and Workflow now have a process_to_future method that can be used to process things into futures.

### Fixes

- Fixed testing to not output large blocks of text.

## v0.1.3

### Changes

- Prompt formatting is now slightly changed to improve prompt inference quality.

### Fixes

- Fixed prompt list to handle indentation and nested lists, tuples and sets.

## v0.1.2

### Changes

- Debug Recorder html output has improved and more condensed formatting.

### Fixes

- Fixed the Debug Recorder to handle quotes and different data types more consistently.
- Fixed retry count exception to use correct variable in message string.

## v0.1.1

### Changes
- DebugRecorder html file improvements

### Fixes
- Fixed pydantic not enforcing field validation

## v0.1.0

### Features

- Improved Testing and Debugging
- Prompts now support array and array_random_order

### Changes

- DebugRecorder method "to_html" renamed to "to_html_file"
- LLM service method "assistant_prompt_str_to_str" renamed to "assistant_str_prompt_to_str"
- Choice LLM Bot now uses array_random_order snippet

### Fixes

- Fixed the prompt title to use a better format.
- Choice LLM Bot has improved default prompts.

## v0.0.10

### Features
- Debug Recorder output to html drastically improved with a lot of new features.

## v0.0.7

### Features
- Added Debug Recorder.

## v0.0.6

### Features
- You can now change set llm_temperature and llm_seed in the LLL Bot for easy customization of each bot.

### Fixes
- Fixed the LlmValidationException to not have arguments

## v0.0.5

### Features
- Llm Config now has more options

### Changes
- Llm Choice Bot now returns a dictionary when using a dictionary instead of a list

### Fixes
- Remove dead utility function for counting estimated tokens in prompts

## v0.0.4

### Features
- Choice Llm Bot can now handle dictionaries Key is used for the choice and the values are returned
- You can now use a Llm config to directly prompt an assistant with a string and return a string

## v0.0.3

### Changes
- Change the structure for Llm config, service and http to be able to handle multiple Llm services easily

## v0.0.2

### Features
- LLM Service Retries
- LLM Prompt Validation Retries
- Single and Multiple Choice LLM Bots added into contributions
- Custom Exceptions that are based on the DandyException
- Much improved testing on base LLM service

# v0.0.1

### Features
- LLM Service
- LLM Prompts
- Bot
- LlmBot
- Workflow

# v0.0.0

### Features
- Initial Release

### Changes
- Initial Release

### Fixes
- Initial Release

# Changelog

## v0.11.0

### Breaking

- All uses of the `process_prompt_to_intel` method now require you to specify either an `intel_class` or an `intel_object` argument.

### Features

- A new example has been created that is much easier to follow and showcases the features of dandy.
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
- Added --version to the CLI interface for dandy.
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

- We have created a new class called `Intel` that is the pydantic `BaseModel` class renamed to give more separation of concerns between dandy code and your code.
- For the most part of this project the word `Model` has been refactored to `Intel` to create more separation of concerns in projects.
- The word `Model` has a lot of meaning in the context of dandy, artificial intelligence, databases, libraries and other frameworks.
- Our hope is this creates a very clear line between these specific objects and the rest of your code.

## v0.7.0

### Major Improvement

- All the changes in v0.7.0 should reduce the over all code required to work with dandy by up to 50%.

### Features

- Project structure improvement with new settings file.
- All projects going forward will require a `dandy_settings.py` file in the root of your project.
  - This file will also need a `BASE_PATH` str variable set to the root of your project.
  - This file will also need a `LLM_CONFIGS` dict variable with a `DEFAULT` llm config.
- Debug recorder can now output to a json string or file.
- Added randomize seed to LLM config that will randomize the seed every time the config is used.
- Added new evaluate cli command for evaluating your dandy code -e --evaluate.
  - Currently only supports Prompt evaluation.
- ALLOW_DEBUG_RECORDING was added to the settings for project wide control of the debug recorder.
  - defaulted to False.
- You can now select your llm config from the cli using the -l --llm-config flag.

### Changes

- Updated the readme to match the new project structure.
- All settings and llm configs are now managed through the dandy settings module.
  - The environment variable `DANDY_SETTINGS_MODULE` can be used to specify the settings module to be used.
  - The system will default to look for a `dandy_settings.py` file in the current working directory or sys.path.
- Moved a lot of project wide constants into the `const.py` file.

### Fixes

- Fixed the user `dandy_settings.py` not loading properly with in the internal dandy modules.
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

- You can now run simple assistant prompts with the -t --test argument for the dandy cli.
  - Example: dandy -t `some.module.cool_llm_bot.CoolLlmBot`

## v0.4.1

### Features

- You can now run simple assistant prompts with the -a --assistant argument for the dandy cli.
  - Example: dandy -a `Hello, how are you?`

## v0.4.0

### Features

- Added a dandy command line interface.
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


# Changelog

## v0.9.1

### Fixes

- Added default instructions prompt to the "LlmBot" class.


## v0.9.0

### Features

- LlmBots now have a default built in process method that takes in a prompt and returns an intel object.
- Changed our http handling library to httpx.
- The contrib choice llm bot has been replaced with the much simpler selector llm bot.
- The Prompt class init now has a text argument that will create a prompt with a text snippet automatically for simple prompts.
- New setting "DEFAULT_LLM_REQUEST_TIME_OUT" that controls the timeout for LLM requests default is "None".

### Changes

- Moved "llm_bot" from "dandy.bot" to "dandy.llm.bot" to match our refactoring changes.
- Changed the base class from "Handler" to "BaseProcessor"
- Refactored "Intel" to "BaseIntel" to improve readability.
- Added "BaseLlmBot" class to "dandy.llm.bot" to be used for creating all llm bots.
- "BaseLlmBot" config now takes just a string that is one of the "LLM_CONFIGS" in the settings.

### Fixes

- There is now a "DefaultLlmIntel" class that is used as the default intel class for LlmBots that has one attribute called "text".
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

- We have created a new class called "Intel" that is the pydantic "BaseModel" class renamed to give more separation of concerns between dandy code and your code.
- For the most part of this project the word "Model" has been refactored to "Intel" to create more separation of concerns in projects.
- The word "Model" has a lot of meaning in the context of dandy, artificial intelligence, databases, libraries and other frameworks.
- Our hope is this creates a very clear line between these specific objects and the rest of your code.

## v0.7.0

### Major Improvement

- All the changes in v0.7.0 should reduce the over all code required to work with dandy by up to 50%.

### Features

- Project structure improvement with new settings file.
- All projects going forward will require a "dandy_settings.py" file in the root of your project.
  - This file will also need a "BASE_PATH" str variable set to the root of your project.
  - This file will also need a "LLM_CONFIGS" dict variable with a "DEFAULT" llm config.
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
  - The environment variable "DANDY_SETTINGS_MODULE" can be used to specify the settings module to be used.
  - The system will default to look for a "dandy_settings.py" file in the current working directory or sys.path.
- Moved a lot of project wide constants into the "const.py" file.

### Fixes

- Fixed the user "dandy_settings.py" not loading properly with in the internal dandy modules.
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
  - Example: dandy -t "some.module.cool_llm_bot.CoolLlmBot"

## v0.4.1

### Features

- You can now run simple assistant prompts with the -a --assistant argument for the dandy cli.
  - Example: dandy -a "Hello, how are you?"

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

- Fixed prompt list to handle indention and nested lists, tuples and sets.

## v0.1.2

### Changes

- Debug Recorder html output has improved and more condensed formating.

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
- Change the structure for Llm config, service and http to be able to handle mutiple Llm services easily

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

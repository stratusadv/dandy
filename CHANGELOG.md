# Changelog

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

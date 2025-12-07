# Changelog

## v1.4.0

### Features

- `FileService` is now available on `Bot` to make it easy to manipulate and work with files.
- The command line interface is back and better than ever, check it out by typing `dandy` in your terminal.
  - Type into the input to learn more about the features.
  - Use `/` to run a command.
- The `BaseIntel` has some new convenience methods `save_to_file` and `create_from_file` for easy long-term storage.

## v1.3.6

### Feature

- Added `lb` method to `Prompt` to clean up verbosity in prompting.

## v1.3.5

### Fixes

- Fixed the `Decoder` prompt and intel classes to properly match each other.

## v1.3.4

### Fixes

- Cleaned up the default `llm_role` and `llm_task` instructions to be more generic and less intrusive.
- Cleaned up the `Decoder` system prompt to be more accurate.
- Cleaned the main llm service system prompt to improve results across `Dandy`. 
- Added the missing line break when adding a `Prompt` to a `Prompt` for better formatting.
- Changed the formatting on the `Decoder` prompt to produce better results when there is no `max_return_values`
- Fixed a bug with decoder not rendering recorder events properly.
- Corrected recorder failing to render `OpenaiRequestMessage` structure.
- Fixed the problem with setting custom attributes on instantiating processors.

## v1.3.3

### Fixes

- Fixed bug causing `system_override_prompt` to not be handled properly in the llm service.

## v1.3.2

### Fixes

- Fixed the `system_prompt_override` to properly override the system prompt.
- Fixed the Decoder prompt to properly show plural when there is no key limit.

## v1.3.1

### Fixes

- Fixed and order of operations mistake with generating the llm service system prompt.

## v1.3.0

### Breaking

- Service method `llm.prompt_to_intel` no longer takes `postfix_system_prompt` as an argument as its redundant.

### Features

- All `Processor` classes `Bot`, `Agent` and `Decoder` now have a `reset_services` method.
  - This provides an easy and lightweight way to reset any persistent data in all the processor services.
- All `Service` classes `Llm`, `Http`, `Intel` now have a `reset_service` method.
  - This is for having more fine control over persistent data.
  - there are other more fine control reset methods, and we recommend you check out the API reference.

### Fixes

- Fixed the signatures for `__init__` method on `Agent`, `Bot` and `Decoder`.
- Correct the order of operation for when message history adds responses in the llm service.

## v1.2.2

### Changes

- After much evaluation of different HTTP libraries and testing we found `requests` was the best option for Dandy.

## v1.2.1

### Fixes

- Fixed the way `Agent` handles processors in the `ProcessorStrategy` and `ProcessorController`.
- Corrected a bug where invalid JSON schemas would get sent by `Agent` when using `Bot.process` with an invalid signature.
- Updated the `IntelFactory` to properly validate JSON schemas.

## v1.2.0

### Features

- `AsyncFuture` has been improved to better handle race conditions and more non-synchronous operations.
- New `process_to_future` function added to allow easy creation of your own futures in your project.
- Service `http` now available on `Agent` and `Bot` for easy interactions with HTTP.
- New setting `FUTURES_MAX_WORKERS` with a default value of `10` for controlling system performance.

### Changes

- Refactored `async_executor` to `thread_pool_executor`.
- Changed the setting `HTTP_CONNECTION_RETRY_COUNT` to default to `4`.
- The `Agent` now uses `TypedBot` instead of `Bot` as a default for `processors` 

### Fixes

- Removed unused argument in `SqliteCache.destroyall` method.
- Better management of the thread pool executor used for handling futures.
- Optimized `Prompt.directory_list` to be more efficient.
- Strategically moved coverage up to 94% improving previous tests and covering more edge cases.
- Improved typing and type handling in `dandy.core.typing` to be more compatible and flexible.
- Added proper handling of `httpx.TimeoutException` to provide better debugging.
- Reworded a lot of the prompts built into Dandy to improve responses and error correction.

## v1.1.5

### Changes

- Change the setting `HTTP_CONNECTION_TIMEOUT_SECONDS` to default to `120`.
- Refactor project structure and configuration files.
- Adjust the testing module structure to match the current dandy structure.

### Fixes

- Fixed `AsyncFuture` to work with `process` methods to not hang indefinitely when returning `None`.
- Removed requirement `request` and switched to `httpx`.
- Correct the `UnionType` type to convert to `Union` when using the `BaseIntel.model_inc_ex_class_copy`.
- Fixed a bug with `BaseIntel.model_inv_ex_class_copy` not parsing default values correctly.
- Update documentation to work properly with dandy v1.

## v1.1.4

### Fixes

- Removed requirement `httpx` and switched to `requests` due to `AsyncFuture` issues causing lockups.

## v1.1.3

### Fixes

- Fixed a memory race condition when using `process_to_future` method that was caused by `httpx.Client`.

## v1.1.2

### Fixes

- Fixed a typing signature problem in `Bot` with the `process` method.

## v1.1.1

### Fixes

- Fixed a problem with all `Mixin` classes conflicting with their processor class.

## v1.1.0

### Features

- `Prompt` has a new method `directory_list` that lets you add the contents of a directory to your prompt.

### Changes

- HTTP Request `Authorization` header only uses the standard `Bearer` token format for handling API keys.

### Fixes

- Updated `LLM_CONFIG` to support putting url paths in the `HOST` key for support of different endpoints.

## v1.0.0

### Major Release

- This is a major release, and we highly recommend reading our documentation before upgrading. 

### Breaking

- Almost all the Dandy API has been refactored in v1 and is not compatible with the v0 API.
- Support for Python 3.10 has been dropped and now requires 3.11 or greater.
- `Workflow` has been removed as we felt it was redundant and there are better more pythonic options.
- `Map` has been refactored to `Decoder` to increase the separation of concerns and describe its function more accurately.
- `Bot`, `Decoder` and `Agent` are now designed to operate instance-based instead of class-based.
- Dandy settings files have had some refactoring and will need to be refactored for `v0` upgrades.

### Features

- `Decoder` previously `Map` is now a stand-alone processor that is much easier to operate and chain.
- New setting `HTTP_CONNECTION_TIMEOUT_SECONDS` takes an `int` and is defaulted to `None`
- New `IntelService` available in the `Bot` for generating and controlling `BaseIntel` classes and objects. 

### Changes

- Refactored all imports from a mix of `typing_extensions` and `typing` to `typing` exclusively.
- All `processor` based objects must be instance operated instead of class operated.
- `llm_instructions` has been broken down into `llm_role`, `llm_task` and `llm_guidelines`
  - All of these accept `Prompt` or `str` and it's recommended to use all 3 but only `llm_role` is required.
- Settings that were prefixed with `DEFAULT_` have all be renamed see `dandy.default_settings.py` for more details.
- Many `DandyExceptions` have been elevated to `Recoverable` to help developers make more robust applications.


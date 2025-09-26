# Changelog

## v1.0.0

### Major Release

- This is a major release, and we highly recommend reading our documentation before upgrading. 

### Breaking

- Almost all the Dandy API has been refactored in v1 and is not compatible with the v0 API.
- Support for Python 3.10 has been dropped and now requires 3.11 or greater.
- `Workflow` has been removed as we felt it was redundant and there are better more pythonic options.
- `Bot`, `Map` and `Agent` are now designed to operate instance based instead of class based. 

### Features

- `Map` is now a stand-alone processor that is much easier to operate and chain.
- New setting `HTTP_CONNECTION_TIMEOUT_SECONDS` takes an `int` and is defaulted to `120`
- New `IntelService` available in the `Bot` for generating and controlling `BaseIntel` classes and objects. 

### Changes

- Refactored all imports from a mix of `typing_extensions` and `typing` to `typing` exclusively.
- All `processor` based objects must be instance operated instead of class operated.
- `llm_instructions` has been broken down into `llm_role`, `llm_task` and `llm_guidelines`
  - All of these accept `Prompt` or `str` and it's recommended to use all 3 but only `llm_role` is required.
- Settings that were prefixed with `DEFAULT_` have all be renamed see `dandy.default_settings.py` for more details.


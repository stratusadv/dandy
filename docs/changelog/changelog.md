# Changelog

## v1.0.0a1

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

### Changes

- Refactored all imports from a mix of `typing_extensions` and `typing` to `typing` exclusively.
- All `processor` based objects must be instance operated instead of class operated.



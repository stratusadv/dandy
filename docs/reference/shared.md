# Shared Kernel

The shared kernel is the only code every layer may depend on. It holds the cross-cutting
building blocks that belong to no single bounded context: the base exception hierarchy,
the [service pattern](../architecture/service_pattern.md) base classes, the settings
loader, file and media utilities, the typing bridge that turns Python signatures into
Intel classes, and the version constants.

Rules for the kernel: it may not import from `domain`, `application`, `infrastructure`,
or `interfaces`. If a type you want to share is specific to one context, it does not
belong here.

## Public API

The `dandy` package root is a thin re-export layer for the public surface. User code
imports from the root; framework code imports from the defining module.

::: dandy

## Exceptions

::: dandy.shared.exceptions

## The service pattern

The bases for the [three-part service pattern](../architecture/service_pattern.md)
(documented there): a lazily built, cached service owned through a mixin, with
`ServiceCriticalError` guarding required class attributes.

::: dandy.shared.service.service.BaseService
    members:
        - obj
        - recorder_event_id
        - reset

::: dandy.shared.service.mixin.BaseServiceMixin
    members:
        - _required_attrs
        - _get_service_instance

::: dandy.shared.service.exceptions

## Connectors

::: dandy.shared.connector.connector.BaseConnector

::: dandy.shared.connector.exceptions

## Settings

`DandySettings` is the settings singleton: on import it loads the user settings module
named by `DANDY_SETTINGS_MODULE` (default `dandy_settings`), falls back to a `dandy.json`
file, and falls back to the defaults. See [Configuration](../getting_started/configuration.md)
for the full resolution order.

::: dandy.shared.conf.settings.DandySettings
    options:
        members:
            - load_user_settings
            - reload_from_os

::: dandy.shared.conf.utils
    options:
        members:
            - get_settings_module_name
            - get_cli_llm_config
            - find_settings_json_file
            - load_settings_from_json_file

::: dandy.shared.conf.default_settings

## File utilities

Pure filesystem helpers shared across layers (the infrastructure file service and the
domain prompt builder both use them).

::: dandy.shared.files
    options:
        members:
            - append_to_file
            - clean_file_extensions
            - encode_file_to_base64
            - file_exists
            - get_file_path_or_exception
            - get_directory_path_or_exception
            - get_directory_listing
            - get_file_extension_from_url_string
            - make_directory
            - read_from_file
            - remove_directory
            - remove_file
            - write_to_file

## Media utilities

Format and MIME detection for image and audio payloads (base64 in, format out).

::: dandy.shared.media
    options:
        members:
            - get_audio_format_from_base64_string
            - get_audio_mime_type_from_base64_string
            - get_image_format_from_base64_string
            - get_image_mime_type_from_base64_string

## Subprocess

The command-execution primitive that tools use: `BaseTool.run_subprocess` applies the
tool's `working_directory` / `timeout_seconds` / `use_shell` and delegates here. It
never raises; failures come back as an `Error: ...` string the model can react to.

::: dandy.shared.subprocess.run_subprocess

## Typing bridge

The machinery that derives pydantic Intel classes from callable signatures and JSON
schemas. `IntelFactory` and `IntelService` (in the domain) are the public entry points;
this is what they call.

::: dandy.shared.typing.typed_kwargs.TypedKwargs

::: dandy.shared.typing.tools
    options:
        members:
            - get_typed_kwargs_from_callable_signature
            - get_typed_kwargs_from_simple_json_schema

::: dandy.shared.typing.registry
    options:
        members:
            - TYPE_REGISTRY
            - resolve_type_from_registry

## Miscellany

::: dandy.shared.singleton.Singleton

::: dandy.shared.utils
    options:
        members:
            - pascal_to_title_case
            - generate_recorder_event_id
            - generate_forwardable_kwargs_if_not_none
            - pydantic_validation_error_to_str
            - python_obj_to_markdown

::: dandy.shared.constants

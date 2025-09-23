import inspect
import json
from typing import Callable

from dandy.core.typing.consts import TYPE_STRING_TO_ANNOTATION_MAP
from dandy.core.typing.exceptions import TypingRecoverableException, TypingCriticalException
from dandy.core.typing.typed_kwargs import TypedKwargs


def get_typed_kwargs_from_callable_signature(
        callable_: Callable,
        return_defaulted: bool = True,
) -> TypedKwargs:
    signature = inspect.signature(callable_)

    typed_kwargs_dict = {}

    for name, param in signature.parameters.items():
        if param.annotation is inspect._empty:
            message = f'Parameter {name} of {callable_.__qualname__} has no typed annotation'
            raise TypingCriticalException(message)

        if param.default is inspect._empty:
            typed_kwargs_dict[name] = (param.annotation, ...)

        elif return_defaulted and param.default is not inspect._empty:
            typed_kwargs_dict[name] = (param.annotation, param.default)

    return TypedKwargs(typed_kwargs_dict)


def get_typed_kwargs_from_simple_json_schema(
        simple_json_schema: dict | str
) -> TypedKwargs:

    if isinstance(simple_json_schema, str):
        simple_json_schema = json.loads(simple_json_schema)

    typed_kwargs_dict = {}

    try:
        for name, type_ in simple_json_schema.items():
            if isinstance(type_, str):
                typed_kwargs_dict[name] = TYPE_STRING_TO_ANNOTATION_MAP[type_.lower()]

            if isinstance(type_, dict):
                for type_1, type_2 in type_.items():
                    typed_kwargs_dict[name] = dict[
                        TYPE_STRING_TO_ANNOTATION_MAP[type_1.lower()],
                        TYPE_STRING_TO_ANNOTATION_MAP[type_2.lower()]
                    ]
                    break

            if isinstance(type_, list):
                if len(type_) > 0:
                    typed_kwargs_dict[name] = list[
                        TYPE_STRING_TO_ANNOTATION_MAP[type_[0]]
                    ]
                else:
                    typed_kwargs_dict[name] = list


    except KeyError:
        message = f'Type {simple_json_schema_str} is not recognized'
        raise TypingRecoverableException(message)

    return TypedKwargs(typed_kwargs_dict)

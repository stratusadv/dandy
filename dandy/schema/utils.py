import json
from typing import Type, Union, get_type_hints

SCHEMA_TO_JSON = {
    str: 'string',
    int: 'integer',
    float: 'number',
    bool: 'boolean',
    list: 'array',
    tuple: 'array',
    dict: 'object',
}


def get_json_type(
        python_type: Union[
            Type[str],
            Type[int],
            Type[float],
            Type[bool],
            Type[list],
            Type[tuple],
            Type[dict]
        ]
) -> str:
    return SCHEMA_TO_JSON[python_type]


def class_to_json_schema_dict(klass) -> dict:
    json_schema = dict()

    for attribute_name, attribute_type in get_type_hints(klass).items():
        json_schema[attribute_name] = get_json_type(attribute_type)

    return json_schema


def class_to_json_schema(klass) -> str:
    return json.dumps(class_to_json_schema_dict(klass), indent=4)
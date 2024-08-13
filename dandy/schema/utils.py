from typing import Type, Union

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

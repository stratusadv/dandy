import json
import traceback

from datetime import date
from typing import Union, Tuple, List
from urllib.parse import quote


def dict_to_str_nicely(dict_data: dict) -> str:
    return json.dumps(dict_data, indent=4)


def encode_parameters(args: Union[List[str], Tuple[str]]):
    for arg in args:
        if isinstance(arg, str):
            yield quote(arg)
        elif isinstance(arg, date):
            yield quote(arg.strftime("%Y-%m-%d"))

    return [quote(arg) for arg in args]


def exception_to_str_nicely(ex: Exception) -> str:
    return '\n'.join([
        ''.join(traceback.format_exception_only(None, ex)).strip(),
        ''.join(traceback.format_exception(None, ex, ex.__traceback__)).strip()
    ])


def lower_dict_keys(dictionary: dict) -> dict:
    return {k.lower(): v for k, v in dictionary.items()}


def print_dict_nicely(dict_data: dict):
    print(dict_to_str_nicely(dict_data))


def print_json_nicely(json_data: str):
    print_dict_nicely(json.loads(json_data))


def print_structure_data_nicely(structure_data: 'Schema'):
    print_json_nicely(structure_data.to_json())


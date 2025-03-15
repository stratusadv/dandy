import base64
from pathlib import Path

from pydantic import ValidationError
from typing_extensions import Union

from dandy.core.exceptions import DandyCriticalException
from dandy.intel import BaseIntel


def encode_file_to_base64(file_path: Union[str, Path]) -> str:
    if not Path(file_path).is_file():
        raise DandyCriticalException(f'File "{file_path}" does not exist')

    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def json_default(obj):
    if isinstance(obj, BaseIntel):
        return obj.model_dump()
    else:
        try:
            return str(obj)
        except TypeError:
            return '<unserializable value>'


def pydantic_validation_error_to_str(error: ValidationError) -> str:
    return error.__str__()



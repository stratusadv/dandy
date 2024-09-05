from __future__ import annotations

import traceback

from datetime import date
from typing import Union, Tuple, List, TYPE_CHECKING
from urllib.parse import quote


if TYPE_CHECKING:
    from dandy.llm.prompt import Prompt


def encode_path_parameters(args: Union[List[str], Tuple[str]]):
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


def get_prompt_estimated_token_count(prompt: Prompt) -> int:
    from dandy import config

    return config.active_llm_service.get_estimated_token_count_for_prompt(
        prompt=prompt
    )



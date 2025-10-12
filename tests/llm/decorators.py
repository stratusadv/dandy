from functools import wraps
from typing import Callable

from tests.consts import TESTING_LLM_CONFIGS


def run_llm_configs(llm_configs: list[str] = TESTING_LLM_CONFIGS) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> None:
            for llm_config in llm_configs:
                print(f'\nRunning {func.__qualname__} with "{llm_config}" llm config ...')
                func(
                    self,
                    llm_config,
                    *args,
                    **kwargs
                )

        return wrapper

    return decorator

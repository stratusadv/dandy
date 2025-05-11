from functools import wraps

from tests.constants import TESTING_LLM_CONFIGS


def run_llm_configs(llm_configs: list[str] = TESTING_LLM_CONFIGS):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for llm_config in llm_configs:
                print(f'Running {func.__qualname__} with "{llm_config}" llm config ...')
                func(
                    self,
                    llm_config,
                    *args,
                    **kwargs
                )

        return wrapper

    return decorator

from abc import ABC
from typing import Any


class BaseConfig(ABC):
    _config_values: set = set()

    def register_setting(
            self,
            name: str,
    ):
        self._config_values.add(name)

    def register_settings(
            self,
            *names: str,
    ):
        for name in names:
            self.register_setting(name)

    @staticmethod
    def default_value_if_none(
            value: Any,
            default_value: Any
    ) -> Any:
        if value is None:
            return default_value
        else:
            return value
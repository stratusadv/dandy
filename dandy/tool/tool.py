from abc import ABC, abstractmethod
from typing import Any, Callable

from dandy.intel.factory import IntelFactory
from dandy.intel.intel import BaseIntel
from dandy.tool.exceptions import ToolCriticalError

ToolHandler = Callable[[BaseIntel | str], str | BaseIntel]


class BaseTool(ABC):
    """Base class for defining tools.

    Subclasses define the tool's name, description and must override the
    abstract handle method whose typed signature becomes the tool's parameter
    schema. The validated arguments are passed to handle as keyword arguments,
    so tools need no dedicated Intel class.

    Example:
        class GetWeatherTool(BaseTool):
            name = 'get_weather'
            description = 'Get the current weather for a location.'

            def handle(self, location: str = '', units: str = 'celsius') -> str:
                return f'The weather in {location} is {units}.'

    """

    name: str = ''
    description: str = ''

    def __init__(self) -> None:
        self._handle_signature_intel_class: type[BaseIntel] | None = None
        self.__post_init__()

    def __post_init__(self) -> None:  # noqa: B027
        pass

    def get_parameters_intel_class(self) -> type[BaseIntel]:
        intel_class = self._handle_signature_intel_class

        if intel_class is None:
            intel_class = IntelFactory.callable_signature_to_intel_class(self.handle)
            self._handle_signature_intel_class = intel_class

        return intel_class

    @abstractmethod
    def handle(self, **kwargs: Any) -> str | BaseIntel:
        """Execute the tool for the given keyword arguments.

        Subclasses override this with typed named parameters; the signature
        becomes the tool's parameter schema and the validated arguments arrive
        as keyword arguments.
        """
        message = f'"{self.__class__.__name__}" does not implement a "handle" method.'
        raise NotImplementedError(message)

    def to_function_dict(self) -> dict:
        if not self.name:
            message = (
                f'"{self.__class__.__name__}" does not have a "name" attribute, '
                f'every BaseTool subclass must define one.'
            )
            raise ToolCriticalError(message)

        parameters_intel_class = self.get_parameters_intel_class()

        return {
            'type': 'function',
            'function': {
                'name': self.name,
                'description': self.description,
                'parameters': IntelFactory.intel_to_json_inc_ex_schema(parameters_intel_class),
            },
        }


ToolType = type[BaseTool] | BaseTool


def to_tool_instances(tools: list[ToolType] | None) -> list[BaseTool]:
    """Normalize tool classes and instances into a list of instances.

    Accepts subclasses of BaseTool, instances of BaseTool, or a mix of
    both, so callers can pass tools the same way they pass Bot subclasses.
    """
    return [tool() if isinstance(tool, type) else tool for tool in tools or []]

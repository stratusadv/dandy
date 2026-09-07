from typing import Callable

from dandy.intel.factory import IntelFactory
from dandy.intel.intel import BaseIntel
from dandy.tool.exceptions import ToolCriticalError

ToolHandler = Callable[[BaseIntel | str], str | BaseIntel]


class BaseTool:
    """Base class for defining tools.

    Subclasses define the tool's name and parameters as class attributes, in the
    same style as Bot exposes role and task. Parameters always derive from an
    Intel class, optionally sliced by include_fields or exclude_fields.

    Example:
        class GetWeatherTool(BaseTool):
            name = 'get_weather'
            description = 'Get the current weather for a location.'
            intel_class = WeatherIntel

            def handle(self, weather_intel: WeatherIntel) -> str:
                return f'The weather in {weather_intel.location} is nice.'

    """

    name: str = ''
    description: str = ''
    intel_class: type[BaseIntel] | None = None
    include_fields: set | dict | None = None
    exclude_fields: set | dict | None = None

    def __init__(self) -> None:
        self.__post_init__()

    def __post_init__(self) -> None:
        pass

    def get_parameters_intel_class(self) -> type[BaseIntel] | None:
        if self.intel_class is None:
            return None

        if self.include_fields or self.exclude_fields:
            return self.intel_class.model_inc_ex_class_copy(
                include=self.include_fields,
                exclude=self.exclude_fields,
            )

        return self.intel_class

    def handle(self, arguments: BaseIntel) -> str | BaseIntel:  # noqa: ARG002
        """Execute the tool for the given arguments.

        Subclasses override this to make the tool self-contained and reusable.
        The default implementation raises so tools without a handle can be
        paired with an external tool_functions mapping instead.
        """
        message = (
            f'"{self.__class__.__name__}" does not implement a "handle" method, '
            f'override "handle" on the tool class or provide a tool function '
            f'via tool_functions.'
        )
        raise ToolCriticalError(message)

    def to_function_dict(self) -> dict:
        if not self.name:
            message = (
                f'"{self.__class__.__name__}" does not have a "name" attribute, '
                f'every BaseTool subclass must define one.'
            )
            raise ToolCriticalError(message)

        parameters_intel_class = self.get_parameters_intel_class()

        parameters = {}

        if parameters_intel_class is not None:
            parameters = IntelFactory.intel_to_json_inc_ex_schema(
                parameters_intel_class
            )

        return {
            'type': 'function',
            'function': {
                'name': self.name,
                'description': self.description,
                'parameters': parameters,
            },
        }


ToolType = type[BaseTool] | BaseTool


def to_tool_instances(
    tools: list[ToolType] | None,
) -> list[BaseTool]:
    """Normalize tool classes and instances into a list of instances.

    Accepts subclasses of BaseTool, instances of BaseTool, or a mix of
    both, so callers can pass tools the same way they pass Bot subclasses.
    """
    return [
        tool() if isinstance(tool, type) else tool
        for tool in tools or []
    ]

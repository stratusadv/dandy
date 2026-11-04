from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable

from dandy.domain.intel.factory import IntelFactory
from dandy.domain.intel.intel import BaseIntel
from dandy.domain.tool.exceptions import ToolCriticalError
from dandy.shared.cancellation import StopSignal
from dandy.shared.subprocess import run_subprocess

ToolHandler = Callable[[BaseIntel | str], str | BaseIntel]


class BaseTool(ABC):
    """Base class for defining tools.

    Subclasses define the tool's name, description and must override the
    abstract handle method whose typed signature becomes the tool's parameter
    schema. The validated arguments are passed to handle as keyword arguments,
    so tools need no dedicated Intel class.

    An optional action_label class attribute names the tool's running beat
    (for example, 'Reading'); without one, the title-cased tool name is used.
    The optional action_output method builds the per-call detail shown next to
    the label while the tool runs, from the validated keyword arguments. The
    can_mutate_state class attribute (default False) marks tools that can
    change state; the CLI renders their beat labels in orange. The
    emits_story_beat class attribute (default True) controls whether the tool's
    execution beat is emitted at all; a tool that renders its own story while
    it runs, like the CLI's question prompt, sets it to False.

    Example:
        class GetWeatherTool(BaseTool):
            name = 'get_weather'
            description = 'Get the current weather for a location.'

            def handle(self, location: str = '', units: str = 'celsius') -> str:
                return f'The weather in {location} is {units}.'

    """

    name: str = ''
    description: str = ''
    action_label: str = ''
    can_mutate_state: bool = False
    emits_story_beat: bool = True

    timeout_seconds: int = 30
    use_shell: bool = False

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

    def action_output(self, **_kwargs: Any) -> str | None:
        """Optional per-call detail shown next to `action_label` while the tool runs.

        Subclasses may override this to return the specifics of the current
        call (for example, 'src/foo.py lines 1-10') so UIs can show exactly
        what the tool is doing. Validated arguments arrive as keyword
        arguments. The default returns None, meaning the label stands alone.
        """
        return None

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

    @property
    def working_directory(self) -> Path:
        """Directory that subprocess commands run in; override per tool."""
        return Path.cwd()

    def run_subprocess(
        self,
        command: list[str] | str,
        timeout_seconds: int | None = None,
        stop_signal: StopSignal | None = None,
    ) -> str:
        """Run a command in `working_directory` and return its output as a string.

        A convenience around the module-level `run_subprocess` that applies this
        tool's `working_directory`, `timeout_seconds`, and `use_shell` settings.
        When `stop_signal` is given, the command is killed promptly if the user
        asks to stop the run.
        """
        resolved_timeout = timeout_seconds if timeout_seconds is not None else self.timeout_seconds

        return run_subprocess(
            command=command,
            cwd=self.working_directory,
            timeout_seconds=resolved_timeout,
            use_shell=self.use_shell,
            stop_signal=stop_signal,
        )


ToolType = type[BaseTool] | BaseTool


def to_tool_instances(tools: list[ToolType] | None) -> list[BaseTool]:
    """Normalize tool classes and instances into a list of instances.

    Accepts subclasses of BaseTool, instances of BaseTool, or a mix of
    both, so callers can pass tools the same way they pass Bot subclasses.
    """
    return [tool() if isinstance(tool, type) else tool for tool in tools or []]

import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable

from dandy.intel.factory import IntelFactory
from dandy.intel.intel import BaseIntel
from dandy.tool.exceptions import ToolCriticalError

ToolHandler = Callable[[BaseIntel | str], str | BaseIntel]

_COMMAND_OUTPUT_CHARACTER_LIMIT = 8000


def run_subprocess(
    command: list[str] | str, cwd: Path, timeout_seconds: int, use_shell: bool = False
) -> str:
    """Run a command and return its output, never raising.

    Output is capped to `_COMMAND_OUTPUT_CHARACTER_LIMIT` characters and
    combined stdout/stderr are prefixed with an exit-code line.
    """

    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            shell=use_shell,
            check=False,
        )

    except subprocess.TimeoutExpired:
        return f'Error: command timed out after {timeout_seconds} seconds.'

    except OSError as error:
        return f'Error: failed to run command: {error}'

    output = completed.stdout or ''
    error_output = completed.stderr or ''

    if output and error_output:
        combined = f'STDOUT:\n{output}\nSTDERR:\n{error_output}'
    elif error_output:
        combined = f'STDERR:\n{error_output}'
    else:
        combined = output

    if len(combined) > _COMMAND_OUTPUT_CHARACTER_LIMIT:
        combined = combined[:_COMMAND_OUTPUT_CHARACTER_LIMIT] + '\n... (truncated)'

    return f'Exit code: {completed.returncode}\n{combined}'


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

    def action_sentence(self, **_kwargs: Any) -> str | None:
        """Optional one-sentence description of what the tool is about to do.

        Subclasses may override this to return a short, present-tense sentence
        (for example, 'Reading src/foo.py.') so UIs can show the exact action
        while the tool runs. Validated arguments arrive as keyword arguments,
        so the sentence can name the specific files, paths, or commands. The
        default returns None, meaning no per-tool sentence is shown.
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

    def run_subprocess(self, command: list[str] | str, timeout_seconds: int | None = None) -> str:
        """Run a command in `working_directory` and return its output as a string.

        A convenience around the module-level `run_subprocess` that applies this
        tool's `working_directory`, `timeout_seconds`, and `use_shell` settings.
        """
        resolved_timeout = timeout_seconds if timeout_seconds is not None else self.timeout_seconds

        return run_subprocess(
            command=command,
            cwd=self.working_directory,
            timeout_seconds=resolved_timeout,
            use_shell=self.use_shell,
        )


ToolType = type[BaseTool] | BaseTool


def to_tool_instances(tools: list[ToolType] | None) -> list[BaseTool]:
    """Normalize tool classes and instances into a list of instances.

    Accepts subclasses of BaseTool, instances of BaseTool, or a mix of
    both, so callers can pass tools the same way they pass Bot subclasses.
    """
    return [tool() if isinstance(tool, type) else tool for tool in tools or []]

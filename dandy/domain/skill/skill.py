from typing import Callable

from dandy.domain.skill.exceptions import SkillCriticalError


class BaseSkill:
    """Base class for defining skills.

    A skill bundles a prompt (instructions for the model) with a set of
    methods that are exposed to the model as tools. Register a skill active
    and its prompt is always part of the system message and its tools are
    always available; register it passive and the model only sees its name
    and description until it activates the skill, which loads its prompt and
    tools.

    Example:
        class GitSkill(BaseSkill):
            name = 'git'
            description = 'Work with the git repository: status, diffs, history.'
            prompt = 'You are working inside a git repository. Never force-push.'
            active = False
            tools = ['status']

            def status(self) -> str:
                '''Show the working tree status.'''
                return 'on branch main, nothing to commit'

    """

    name: str = ''
    description: str = ''
    prompt: str = ''
    active: bool = True
    tools: list[str] = []

    def __init__(self, active: bool | None = None) -> None:
        if active is not None:
            self.active = active

        self.__post_init__()

    def __post_init__(self) -> None:
        pass

    @property
    def tool_names(self) -> list[str]:
        """The tool names this skill's declared methods are exposed under."""
        return [f'{self.name}_{tool_name}' for tool_name in self.tools]

    def get_method(self, method_name: str) -> Callable:
        """The bound method a declared tool name refers to, validated.

        Raises SkillCriticalError when the method is missing, private, or not
        callable.
        """
        method = getattr(self, method_name, None)

        if method is None or method_name.startswith('_'):
            message = (
                f'Skill "{self.name}" declares "{method_name}" in "tools" '
                f'but no such method exists.'
            )
            raise SkillCriticalError(message)

        if not callable(method):
            message = (
                f'Skill "{self.name}" declares "{method_name}" in "tools" but it is not callable.'
            )
            raise SkillCriticalError(message)

        return method

    def method_description(self, method_name: str) -> str:
        """First docstring line of a declared tool method, with a fallback."""
        docstring = (self.get_method(method_name).__doc__ or '').strip()
        first_line = docstring.splitlines()[0].strip() if docstring else ''

        return first_line or f'{self.name} {method_name}'


SkillType = type[BaseSkill] | BaseSkill


def to_skill_instances(skills: list[SkillType] | None) -> list[BaseSkill]:
    """Normalize skill classes and instances into a list of instances.

    Accepts subclasses of BaseSkill, instances of BaseSkill, or a mix of
    both, so callers can pass skills the same way they pass tools or Bots.
    """
    return [skill() if isinstance(skill, type) else skill for skill in skills or []]

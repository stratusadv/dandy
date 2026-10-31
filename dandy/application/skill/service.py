from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.shared.service.service import BaseService
from dandy.application.skill.tools import ActivateSkillTool, SkillMethodTool
from dandy.domain.skill.exceptions import SkillCriticalError
from dandy.domain.skill.prompts import skill_system_prompt_section
from dandy.domain.skill.skill import BaseSkill, SkillType, to_skill_instances

if TYPE_CHECKING:
    from dandy.domain.tool.tool import BaseTool

ACTIVATE_TOOL_NAME = 'activate_skill'


class SkillService(BaseService['dandy.application.skill.mixin.SkillServiceMixin']):
    """Registry for the skills attached to a bot's LLM service.

    Active skills contribute their prompt to the system message and expose
    their methods as tools from the first request; passive skills contribute
    their name and description until the model activates them with the
    activate_skill tool, after which their prompt has entered the
    conversation and their tools join the tool list. Activation is one-way
    until reset.
    """

    def __post_init__(self) -> None:
        self._skills: list[BaseSkill] = []
        self._activated: set[str] = set()
        self._skill_tools: dict[str, list[BaseTool]] = {}
        self._activate_tool: ActivateSkillTool | None = None

    def register(self, skills: list[SkillType] | None) -> None:
        """Normalize, validate, and add skills to the registry."""
        for skill in to_skill_instances(skills):
            self._validate_skill(skill)
            self._skills.append(skill)
            self._skill_tools[skill.name] = self._build_skill_tools(skill)

    def system_prompt_section(self) -> str:
        """The skills section of the system message (empty when no skills)."""
        return skill_system_prompt_section(self._skills).to_str()

    def active_tools(self) -> list[BaseTool]:
        """Skill method tools currently exposed, plus activate_skill if needed."""
        tools: list[BaseTool] = []

        for skill in self._skills:
            if skill.active or skill.name in self._activated:
                tools.extend(self._skill_tools[skill.name])

        if self._has_unactivated_passive():
            tools.append(self._activate_tool_instance())

        return tools

    def all_tool_names(self) -> set[str]:
        """Every tool name this registry can expose in the current state."""
        names = {tool.name for tools in self._skill_tools.values() for tool in tools}

        if self._has_unactivated_passive():
            names.add(ACTIVATE_TOOL_NAME)

        return names

    def activate(self, name: str) -> str:
        """Activate a passive skill; the return value is the tool result."""
        skill = next((candidate for candidate in self._skills if candidate.name == name), None)

        if skill is None or skill.active:
            available = [candidate.name for candidate in self._skills if not candidate.active]
            available_text = (
                f' Available passive skills: {", ".join(available)}.' if available else ''
            )
            return f'No passive skill named "{name}" was registered.{available_text}'

        if name in self._activated:
            return f'Skill "{name}" is already active; continue following its instructions.'

        self._activated.add(name)

        if skill.prompt:
            return f'Skill "{name}" is now active. Follow the instructions below.\n\n{skill.prompt}'

        return (
            f'Skill "{name}" is now active. It has no additional instructions; '
            f'its tools are now available.'
        )

    def reset(self) -> None:
        self._activated.clear()

    def _validate_skill(self, skill: BaseSkill) -> None:
        if not skill.name:
            message = (
                f'"{skill.__class__.__name__}" does not have a "name" attribute, '
                f'every BaseSkill subclass must define one.'
            )
            raise SkillCriticalError(message)

        if not skill.active and not skill.description:
            message = (
                f'Passive skill "{skill.name}" needs a "description" so the model '
                f'knows when to activate it.'
            )
            raise SkillCriticalError(message)

        if any(other.name == skill.name for other in self._skills):
            message = f'Two registered skills share the name "{skill.name}".'
            raise SkillCriticalError(message)

        existing_tool_names = {tool.name for tools in self._skill_tools.values() for tool in tools}

        for tool_name in skill.tool_names:
            if tool_name == ACTIVATE_TOOL_NAME:
                message = (
                    f'Skill "{skill.name}" generates the tool name '
                    f'"{ACTIVATE_TOOL_NAME}", which is reserved.'
                )
                raise SkillCriticalError(message)

            if tool_name in existing_tool_names:
                message = f'Two registered skills generate the tool name "{tool_name}".'
                raise SkillCriticalError(message)

        for method_name in skill.tools:
            skill.get_method(method_name)

    @staticmethod
    def _build_skill_tools(skill: BaseSkill) -> list[BaseTool]:
        return [
            SkillMethodTool(
                tool_name=f'{skill.name}_{method_name}',
                description=skill.method_description(method_name),
                method=skill.get_method(method_name),
            )
            for method_name in skill.tools
        ]

    def _has_unactivated_passive(self) -> bool:
        return any(not skill.active and skill.name not in self._activated for skill in self._skills)

    def _activate_tool_instance(self) -> ActivateSkillTool:
        if self._activate_tool is None:
            self._activate_tool = ActivateSkillTool(skill_service=self)

        return self._activate_tool

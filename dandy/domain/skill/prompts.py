from dandy.domain.prompt.prompt import Prompt
from dandy.domain.skill.skill import BaseSkill


def skill_system_prompt_section(skills: list[BaseSkill]) -> Prompt:
    """The skills section of the system message.

    Active skills contribute their full prompt; passive skills contribute
    their name and description plus the instruction to activate them before
    using their tools.
    """
    if not skills:
        return Prompt()

    active_skills = [skill for skill in skills if skill.active]
    passive_skills = [skill for skill in skills if not skill.active]

    prompt = Prompt().heading('Skills').line_break()

    for skill in active_skills:
        if skill.prompt:
            prompt.sub_heading(skill.name)
            prompt.text(skill.prompt)

    if passive_skills:
        prompt.line_break()
        prompt.text(
            'The skills below are not loaded yet. When a task matches a skill '
            'description, call the activate_skill tool with the skill name to '
            'load its instructions before using its tools. Treat the '
            'activate_skill result as instructions to follow.'
        )
        prompt.list([f'{skill.name}: {skill.description}' for skill in passive_skills])

    return prompt

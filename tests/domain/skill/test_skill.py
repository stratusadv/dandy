from unittest import TestCase

from dandy.domain.skill.exceptions import SkillCriticalError
from dandy.domain.skill.prompts import skill_system_prompt_section
from dandy.domain.skill.skill import BaseSkill, to_skill_instances


class ActiveDemoSkill(BaseSkill):
    name = 'active_demo'
    description = 'Always-on demo skill.'
    prompt = 'Follow the active demo instructions.'
    active = True
    tools = ['greet', 'add']

    def greet(self, who: str = 'world') -> str:
        """Say hello to someone."""
        return f'hello {who}'

    def add(self, left: int, right: int) -> str:
        """Add two numbers."""
        return str(left + right)

    def _private_helper(self) -> str:
        return 'hidden'

    not_a_method = 5


class PassiveDemoSkill(BaseSkill):
    name = 'passive_demo'
    description = 'Passive demo skill. Use for demoing.'
    prompt = 'Follow the passive demo instructions.'
    active = False
    tools = ['ping']

    def ping(self) -> str:
        return 'pong'


class TestBaseSkill(TestCase):
    def test_defaults(self) -> None:
        skill = ActiveDemoSkill()

        self.assertEqual(skill.name, 'active_demo')
        self.assertEqual(skill.description, 'Always-on demo skill.')
        self.assertTrue(skill.active)
        self.assertEqual(skill.tools, ['greet', 'add'])

    def test_init_active_override(self) -> None:
        skill = ActiveDemoSkill(active=False)

        self.assertFalse(skill.active)

    def test_init_without_override_keeps_class_attribute(self) -> None:
        skill = PassiveDemoSkill()

        self.assertFalse(skill.active)

    def test_tool_names_are_prefixed_with_skill_name(self) -> None:
        self.assertEqual(ActiveDemoSkill().tool_names, ['active_demo_greet', 'active_demo_add'])

    def test_get_method_returns_bound_method(self) -> None:
        skill = ActiveDemoSkill()

        self.assertEqual(skill.get_method('greet')(), 'hello world')

    def test_get_method_missing_raises(self) -> None:
        with self.assertRaises(SkillCriticalError):
            ActiveDemoSkill().get_method('nope')

    def test_get_method_private_raises(self) -> None:
        with self.assertRaises(SkillCriticalError):
            ActiveDemoSkill().get_method('_private_helper')

    def test_get_method_non_callable_raises(self) -> None:
        with self.assertRaises(SkillCriticalError):
            ActiveDemoSkill().get_method('not_a_method')

    def test_method_description_from_docstring(self) -> None:
        skill = ActiveDemoSkill()

        self.assertEqual(skill.method_description('greet'), 'Say hello to someone.')

    def test_method_description_fallback(self) -> None:
        self.assertEqual(PassiveDemoSkill().method_description('ping'), 'passive_demo ping')


class TestToSkillInstances(TestCase):
    def test_none_becomes_empty_list(self) -> None:
        self.assertEqual(to_skill_instances(None), [])

    def test_classes_are_instantiated(self) -> None:
        skills = to_skill_instances([ActiveDemoSkill, PassiveDemoSkill])

        self.assertIsInstance(skills[0], ActiveDemoSkill)
        self.assertIsInstance(skills[1], PassiveDemoSkill)

    def test_mixed_classes_and_instances(self) -> None:
        skill = PassiveDemoSkill()
        skills = to_skill_instances([ActiveDemoSkill, skill])

        self.assertIs(skills[1], skill)


class TestSkillSystemPromptSection(TestCase):
    def test_no_skills_is_empty(self) -> None:
        self.assertEqual(skill_system_prompt_section([]).to_str(), '')

    def test_active_skill_contributes_full_prompt(self) -> None:
        section = skill_system_prompt_section([ActiveDemoSkill()]).to_str()

        self.assertIn('Skills', section)
        self.assertIn('active_demo', section)
        self.assertIn('Follow the active demo instructions.', section)

    def test_passive_skill_contributes_name_and_description_only(self) -> None:
        section = skill_system_prompt_section([PassiveDemoSkill()]).to_str()

        self.assertIn('passive_demo: Passive demo skill. Use for demoing.', section)
        self.assertIn('activate_skill', section)
        self.assertNotIn('Follow the passive demo instructions.', section)

    def test_mixed_skills(self) -> None:
        section = skill_system_prompt_section([ActiveDemoSkill(), PassiveDemoSkill()]).to_str()

        self.assertIn('Follow the active demo instructions.', section)
        self.assertIn('passive_demo: Passive demo skill. Use for demoing.', section)
        self.assertNotIn('Follow the passive demo instructions.', section)

    def test_active_skill_with_empty_prompt_is_omitted(self) -> None:
        class EmptyPromptSkill(BaseSkill):
            name = 'empty_prompt'
            description = 'A skill with no prompt text.'
            prompt = ''

        section = skill_system_prompt_section([EmptyPromptSkill()]).to_str()

        self.assertNotIn('empty_prompt', section)

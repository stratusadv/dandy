from unittest import TestCase

from dandy.application.skill.service import SkillService
from dandy.domain.skill.exceptions import SkillCriticalError
from dandy.domain.skill.skill import BaseSkill
from tests.application.skill.intelligence.skills import NotesSkill, WeatherSkill


def make_skill_service() -> SkillService:
    class Owner:
        pass

    return SkillService(obj=Owner())


class NamelessSkill(BaseSkill):
    description = 'A skill without a name.'
    prompt = 'Do the thing.'


class PassiveNoDescriptionSkill(BaseSkill):
    name = 'silent'
    description = ''
    prompt = 'Do the thing.'
    active = False


class ReservedToolNameSkill(BaseSkill):
    name = 'activate'
    description = 'A skill that collides with the reserved tool name.'
    prompt = 'Do the thing.'
    tools = ['skill']

    def skill(self) -> str:
        return 'bad'


class FirstClashSkill(BaseSkill):
    name = 'clash'
    description = 'First of a colliding pair.'
    prompt = 'First.'
    tools = ['go_now']

    def go_now(self) -> str:
        return 'first'


class SecondClashSkill(BaseSkill):
    name = 'clash_go'
    description = 'Second of a colliding pair.'
    prompt = 'Second.'
    tools = ['now']

    def now(self) -> str:
        return 'second'


class MissingMethodSkill(BaseSkill):
    name = 'missing_method'
    description = 'Declares a method that does not exist.'
    prompt = 'Do the thing.'
    tools = ['nope']


class TestSkillServiceRegister(TestCase):
    def test_no_skills(self) -> None:
        service = make_skill_service()

        self.assertEqual(service.system_prompt_section(), '')
        self.assertEqual(service.active_tools(), [])
        self.assertEqual(service.all_tool_names(), set())

    def test_active_skill_prompt_in_section(self) -> None:
        service = make_skill_service()
        service.register([NotesSkill])

        section = service.system_prompt_section()

        self.assertIn('notes', section)
        self.assertIn('Store notes with notes_save and find them with notes_recall.', section)

    def test_passive_skill_metadata_in_section_not_prompt(self) -> None:
        service = make_skill_service()
        service.register([WeatherSkill])

        section = service.system_prompt_section()

        self.assertIn(
            'weather: Get current weather. Use when the user asks about the weather.', section
        )
        self.assertIn('activate_skill', section)
        self.assertNotIn('Answer weather questions using the weather tool.', section)

    def test_nameless_skill_raises(self) -> None:
        service = make_skill_service()

        with self.assertRaises(SkillCriticalError):
            service.register([NamelessSkill])

    def test_passive_skill_without_description_raises(self) -> None:
        service = make_skill_service()

        with self.assertRaises(SkillCriticalError):
            service.register([PassiveNoDescriptionSkill])

    def test_duplicate_skill_names_raise(self) -> None:
        service = make_skill_service()
        service.register([NotesSkill])

        with self.assertRaises(SkillCriticalError):
            service.register([NotesSkill()])

    def test_duplicate_generated_tool_names_raise(self) -> None:
        service = make_skill_service()
        service.register([FirstClashSkill])

        with self.assertRaises(SkillCriticalError):
            service.register([SecondClashSkill])

    def test_reserved_activate_tool_name_raises(self) -> None:
        service = make_skill_service()

        with self.assertRaises(SkillCriticalError):
            service.register([ReservedToolNameSkill])

    def test_missing_declared_method_raises(self) -> None:
        service = make_skill_service()

        with self.assertRaises(SkillCriticalError):
            service.register([MissingMethodSkill])


class TestSkillServiceActiveTools(TestCase):
    def test_active_skill_tools_from_first_request(self) -> None:
        service = make_skill_service()
        service.register([NotesSkill])

        tool_names = [tool.name for tool in service.active_tools()]

        self.assertIn('notes_save', tool_names)
        self.assertIn('notes_recall', tool_names)
        self.assertNotIn('activate_skill', tool_names)

    def test_passive_skill_tools_hidden_until_activated(self) -> None:
        service = make_skill_service()
        service.register([WeatherSkill])

        tool_names = [tool.name for tool in service.active_tools()]

        self.assertNotIn('weather_current', tool_names)
        self.assertIn('activate_skill', tool_names)

    def test_mixed_registration(self) -> None:
        service = make_skill_service()
        service.register([NotesSkill, WeatherSkill])

        tool_names = [tool.name for tool in service.active_tools()]

        self.assertIn('notes_save', tool_names)
        self.assertNotIn('weather_current', tool_names)
        self.assertIn('activate_skill', tool_names)

    def test_method_tool_schema_from_method_signature(self) -> None:
        service = make_skill_service()
        service.register([NotesSkill])
        save_tool = next(tool for tool in service.active_tools() if tool.name == 'notes_save')

        tool_dict = save_tool.to_function_dict()

        self.assertEqual(tool_dict['function']['name'], 'notes_save')
        self.assertEqual(tool_dict['function']['description'], 'Store a note.')
        parameters = tool_dict['function']['parameters']
        self.assertEqual(set(parameters['properties'].keys()), {'note'})
        self.assertEqual(parameters['properties']['note']['type'], 'string')
        self.assertEqual(parameters['required'], ['note'])

    def test_method_tool_dispatch(self) -> None:
        service = make_skill_service()
        service.register([NotesSkill])
        save_tool = next(tool for tool in service.active_tools() if tool.name == 'notes_save')

        self.assertEqual(save_tool.handle(note='buy milk'), 'Saved: buy milk')


class TestSkillServiceActivate(TestCase):
    def test_activate_returns_prompt_and_exposes_tools(self) -> None:
        service = make_skill_service()
        service.register([WeatherSkill])

        result = service.activate('weather')

        self.assertIn('weather', result)
        self.assertIn('Answer weather questions using the weather tool.', result)

        tool_names = [tool.name for tool in service.active_tools()]
        self.assertIn('weather_current', tool_names)
        self.assertNotIn('activate_skill', tool_names)

    def test_activate_unknown_skill(self) -> None:
        service = make_skill_service()
        service.register([WeatherSkill])

        result = service.activate('nope')

        self.assertIn('No passive skill named "nope"', result)
        self.assertIn('weather', result)

    def test_activate_active_skill_reports_no_passive(self) -> None:
        service = make_skill_service()
        service.register([NotesSkill, WeatherSkill])

        result = service.activate('notes')

        self.assertIn('No passive skill named "notes"', result)

    def test_activate_twice(self) -> None:
        service = make_skill_service()
        service.register([WeatherSkill])
        service.activate('weather')

        result = service.activate('weather')

        self.assertIn('already active', result)

    def test_reset_deactivates_passive_skills(self) -> None:
        service = make_skill_service()
        service.register([WeatherSkill])
        service.activate('weather')

        service.reset()

        tool_names = [tool.name for tool in service.active_tools()]
        self.assertNotIn('weather_current', tool_names)
        self.assertIn('activate_skill', tool_names)

    def test_all_tool_names_tracks_state(self) -> None:
        service = make_skill_service()
        service.register([WeatherSkill])

        self.assertEqual(service.all_tool_names(), {'weather_current', 'activate_skill'})

        service.activate('weather')

        self.assertEqual(service.all_tool_names(), {'weather_current'})

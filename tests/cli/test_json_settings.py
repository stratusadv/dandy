import json
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from dandy.cli.utils import check_or_create_settings
from dandy.conf import settings
from dandy.core.exceptions import DandyCriticalError
from dandy.conf.utils import (
    find_settings_json_file,
    get_settings_json_candidates,
    load_settings_from_json_file,
)

INVALID_SETTINGS_MODULE_NAME = 'no_such_dandy_settings'

JSON_WITH_LLM_CONFIG = {
    'llm_configs': {
        'default': {
            'HOST': 'example.com',
            'PORT': 443,
            'API_KEY': 'test-key',
            'MODEL': 'json_model',
            'OPTIONS': {'temperature': 0.2},
        }
    },
    'cli_config': {'coding': 'default'},
}


def _reset_settings_state() -> None:
    settings._user_settings = ...
    settings._has_loaded_user_settings = False
    settings._json_settings_path = None


class JsonSettingsTestCase(TestCase):
    def setUp(self) -> None:
        self._saved_settings_state = (
            settings._user_settings,
            settings._has_loaded_user_settings,
            settings._json_settings_path,
        )
        _reset_settings_state()

    def tearDown(self) -> None:
        (
            settings._user_settings,
            settings._has_loaded_user_settings,
            settings._json_settings_path,
        ) = self._saved_settings_state


class TestLoadSettingsFromJsonFile(JsonSettingsTestCase):
    def test_normalizes_keys_and_coerces_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory_str:
            temp_directory = Path(temp_directory_str)
            json_file_path = Path(temp_directory, 'settings.json')
            json_file_path.write_text(
                json.dumps(
                    {
                        'base_path': str(temp_directory),
                        'llm_configs': {'default': {'MODEL': 'm', 'API_KEY': 'k', 'HOST': 'h'}},
                        'cli_config': {'coding': 'default'},
                        'ALLOW_RECORDING_TO_FILE': True,
                    }
                )
            )

            namespace = load_settings_from_json_file(json_file_path)

            self.assertEqual(namespace.BASE_PATH, temp_directory)
            self.assertEqual(list(namespace.LLM_CONFIGS.keys()), ['DEFAULT'])
            self.assertEqual(namespace.CLI_CONFIG, {'CODING': 'DEFAULT'})
            self.assertTrue(namespace.ALLOW_RECORDING_TO_FILE)

    def test_uppercases_cli_config_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory_str:
            json_file_path = Path(temp_directory_str, 'settings.json')
            json_file_path.write_text(
                json.dumps({'cli_config': {'coding': 'coding_model', 'vision': None}})
            )

            namespace = load_settings_from_json_file(json_file_path)

            self.assertEqual(namespace.CLI_CONFIG, {'CODING': 'CODING_MODEL', 'VISION': None})

    def test_normalizes_llm_config_inner_keys_but_not_option_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory_str:
            json_file_path = Path(temp_directory_str, 'settings.json')
            json_file_path.write_text(
                json.dumps(
                    {
                        'llm_configs': {
                            'default': {
                                'host': 'example.com',
                                'api_key': 'k',
                                'model': 'm',
                                'options': {'frequency_penalty': 0.5},
                            }
                        }
                    }
                )
            )

            namespace = load_settings_from_json_file(json_file_path)

            default_config = namespace.LLM_CONFIGS['DEFAULT']
            self.assertEqual(list(default_config.keys()), ['HOST', 'API_KEY', 'MODEL', 'OPTIONS'])
            self.assertEqual(default_config['OPTIONS'], {'frequency_penalty': 0.5})

    def test_defaults_base_path_to_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory_str:
            temp_directory = Path(temp_directory_str)
            json_file_path = Path(temp_directory, 'settings.json')
            json_file_path.write_text('{"debug": true}')

            with mock.patch('pathlib.Path.cwd', return_value=temp_directory):
                namespace = load_settings_from_json_file(json_file_path)

            self.assertEqual(namespace.BASE_PATH, temp_directory)
            self.assertTrue(namespace.DEBUG)

    def test_malformed_json_raises_critical_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory_str:
            json_file_path = Path(temp_directory_str, 'settings.json')
            json_file_path.write_text('{invalid')

            with self.assertRaises(DandyCriticalError):
                load_settings_from_json_file(json_file_path)

    def test_non_object_json_raises_critical_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory_str:
            json_file_path = Path(temp_directory_str, 'settings.json')
            json_file_path.write_text('[1, 2, 3]')

            with self.assertRaises(DandyCriticalError):
                load_settings_from_json_file(json_file_path)


class TestSettingsJsonCandidates(TestCase):
    def test_checks_cwd_before_home(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory_str:
            temp_directory = Path(temp_directory_str)

            with (
                mock.patch('pathlib.Path.cwd', return_value=temp_directory),
                mock.patch('pathlib.Path.home', return_value=temp_directory),
            ):
                candidates = get_settings_json_candidates()
                found_file_path = find_settings_json_file()

            self.assertEqual(
                candidates,
                [
                    temp_directory / '.dandy' / 'dandy.json',
                    temp_directory / '.config' / 'dandy' / 'dandy.json',
                ],
            )
            self.assertIsNone(found_file_path)


class TestJsonSettingsFallback(JsonSettingsTestCase):
    def test_loads_from_cwd_dandy_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory_str:
            project_path = Path(temp_directory_str)
            Path(project_path, '.dandy').mkdir()
            Path(project_path, '.dandy', 'dandy.json').write_text(json.dumps(JSON_WITH_LLM_CONFIG))

            with (
                mock.patch(
                    'dandy.conf.settings.get_settings_module_name',
                    return_value=INVALID_SETTINGS_MODULE_NAME,
                ),
                mock.patch('pathlib.Path.cwd', return_value=project_path),
                mock.patch('pathlib.Path.home', return_value=Path(project_path, 'empty_home')),
            ):
                settings.load_user_settings()

            self.assertTrue(settings._has_loaded_user_settings)
            self.assertEqual(
                settings._json_settings_path, Path(project_path, '.dandy', 'dandy.json')
            )
            self.assertEqual(settings.LLM_CONFIGS['DEFAULT']['MODEL'], 'json_model')
            self.assertEqual(settings.CLI_CONFIG['CODING'], 'DEFAULT')
            self.assertEqual(settings.BASE_PATH, project_path)

    def test_loads_from_home_config_when_no_cwd_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory_str:
            temp_directory = Path(temp_directory_str)
            project_path = Path(temp_directory, 'project')
            home_path = Path(temp_directory, 'home')
            project_path.mkdir()
            Path(home_path, '.config', 'dandy').mkdir(parents=True)
            Path(home_path, '.config', 'dandy', 'dandy.json').write_text(
                json.dumps(JSON_WITH_LLM_CONFIG)
            )

            with (
                mock.patch(
                    'dandy.conf.settings.get_settings_module_name',
                    return_value=INVALID_SETTINGS_MODULE_NAME,
                ),
                mock.patch('pathlib.Path.cwd', return_value=project_path),
                mock.patch('pathlib.Path.home', return_value=home_path),
            ):
                settings.load_user_settings()

            self.assertTrue(settings._has_loaded_user_settings)
            self.assertEqual(
                settings._json_settings_path, Path(home_path, '.config', 'dandy', 'dandy.json')
            )
            self.assertEqual(settings.LLM_CONFIGS['DEFAULT']['MODEL'], 'json_model')

    def test_cwd_json_takes_precedence_over_home_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory_str:
            temp_directory = Path(temp_directory_str)
            project_path = Path(temp_directory, 'project')
            home_path = Path(temp_directory, 'home')
            Path(project_path, '.dandy').mkdir(parents=True)
            Path(home_path, '.config', 'dandy').mkdir(parents=True)
            Path(project_path, '.dandy', 'dandy.json').write_text(
                json.dumps(
                    {
                        'llm_configs': {
                            'default': {'MODEL': 'cwd_model', 'API_KEY': 'k', 'HOST': 'h'}
                        }
                    }
                )
            )
            Path(home_path, '.config', 'dandy', 'dandy.json').write_text(
                json.dumps(
                    {
                        'llm_configs': {
                            'default': {'MODEL': 'home_model', 'API_KEY': 'k', 'HOST': 'h'}
                        }
                    }
                )
            )

            with (
                mock.patch(
                    'dandy.conf.settings.get_settings_module_name',
                    return_value=INVALID_SETTINGS_MODULE_NAME,
                ),
                mock.patch('pathlib.Path.cwd', return_value=project_path),
                mock.patch('pathlib.Path.home', return_value=home_path),
            ):
                settings.load_user_settings()

            self.assertEqual(
                settings._json_settings_path, Path(project_path, '.dandy', 'dandy.json')
            )
            self.assertEqual(settings.LLM_CONFIGS['DEFAULT']['MODEL'], 'cwd_model')

    def test_python_module_takes_precedence_over_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory_str:
            project_path = Path(temp_directory_str)
            Path(project_path, '.dandy').mkdir()
            Path(project_path, '.dandy', 'dandy.json').write_text(json.dumps(JSON_WITH_LLM_CONFIG))

            with (
                mock.patch(
                    'dandy.conf.settings.get_settings_module_name',
                    return_value='tests.dandy_settings',
                ),
                mock.patch('pathlib.Path.cwd', return_value=project_path),
            ):
                settings.load_user_settings()

            self.assertTrue(settings._has_loaded_user_settings)
            self.assertIsNone(settings._json_settings_path)

    def test_no_json_no_module_leaves_settings_unloaded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory_str:
            project_path = Path(temp_directory_str)

            with (
                mock.patch(
                    'dandy.conf.settings.get_settings_module_name',
                    return_value=INVALID_SETTINGS_MODULE_NAME,
                ),
                mock.patch('pathlib.Path.cwd', return_value=project_path),
                mock.patch('pathlib.Path.home', return_value=Path(project_path, 'empty_home')),
            ):
                settings.load_user_settings()

            self.assertFalse(settings._has_loaded_user_settings)
            self.assertIsNone(settings._json_settings_path)


class TestCheckOrCreateSettingsJson(JsonSettingsTestCase):
    def test_does_not_create_py_file_when_json_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory_str:
            project_path = Path(temp_directory_str)
            Path(project_path, '.dandy').mkdir()
            Path(project_path, '.dandy', 'dandy.json').write_text(json.dumps({'debug': True}))

            with (
                mock.patch('pathlib.Path.cwd', return_value=project_path),
                mock.patch(
                    'dandy.conf.utils.get_settings_module_name',
                    return_value=INVALID_SETTINGS_MODULE_NAME,
                ),
            ):
                check_or_create_settings(cwd_path=project_path, system_exit_on_import_error=False)

            self.assertFalse(Path(project_path, f'{INVALID_SETTINGS_MODULE_NAME}.py').exists())

    def test_creates_py_file_when_no_json_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory_str:
            project_path = Path(temp_directory_str)

            with (
                mock.patch('pathlib.Path.cwd', return_value=project_path),
                mock.patch(
                    'dandy.conf.utils.get_settings_module_name',
                    return_value=INVALID_SETTINGS_MODULE_NAME,
                ),
            ):
                check_or_create_settings(cwd_path=project_path, system_exit_on_import_error=False)

            created_file_path = Path(project_path, f'{INVALID_SETTINGS_MODULE_NAME}.py')
            self.assertTrue(created_file_path.exists())
            created_file_path.unlink()

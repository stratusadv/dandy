import contextlib
from pathlib import Path
from unittest import TestCase, mock

from dandy.cli.utils import check_or_create_settings, get_cli_llm_config
from dandy.conf import settings

INVALID_SETTINGS_MODULE_NAME = 'tests.invalid_dandy_settings'

BASE_PATH = Path(__file__).parent.parent.parent.resolve()


class TestGetCliLlmConfig(TestCase):
    def test_get_cli_llm_config_uses_cli_config(self) -> None:
        self.assertEqual(get_cli_llm_config('CODING'), 'THINKING')

    def test_get_cli_llm_config_uses_custom_llm_name(self) -> None:
        with mock.patch.object(settings, 'CLI_CONFIG', {'CODING': 'CODING_MODEL'}):
            self.assertEqual(get_cli_llm_config('CODING'), 'CODING_MODEL')

    def test_get_cli_llm_config_falls_back_to_default(self) -> None:
        with mock.patch.object(settings, 'CLI_CONFIG', {'CODING': 'CODING_MODEL'}):
            self.assertEqual(get_cli_llm_config('UNKNOWN_TASK'), 'DEFAULT')

    def test_get_cli_llm_config_handles_missing_config(self) -> None:
        with mock.patch.object(settings, 'CLI_CONFIG', None):
            self.assertEqual(get_cli_llm_config('CODING'), 'DEFAULT')


class TestUtils(TestCase):
    def test_check_or_create_settings(self):
        try:
            check_or_create_settings(cwd_path=BASE_PATH)
        except ImportError:
            self.fail('check_or_create_settings() raised ImportError unexpectedly!')

    def test_check_or_create_settings_invalid_settings_module_name(self):
        with (
            mock.patch(
                'dandy.conf.utils.get_settings_module_name',
                return_value=INVALID_SETTINGS_MODULE_NAME,
            ),
            contextlib.suppress(ImportError),
        ):
            check_or_create_settings(cwd_path=BASE_PATH, system_exit_on_import_error=False)

        with mock.patch(
            'dandy.conf.utils.get_settings_module_name', return_value=INVALID_SETTINGS_MODULE_NAME
        ):
            try:
                check_or_create_settings(cwd_path=BASE_PATH)
            except ImportError:
                self.fail(
                    'check_or_create_settings() did not properly handle invalid settings module name!'
                )

            finally:
                settings_file_path_segments = INVALID_SETTINGS_MODULE_NAME.split('.')

                invalid_settings_path = (
                    BASE_PATH
                    / settings_file_path_segments[0]
                    / f'{settings_file_path_segments[1]}.py'
                )

                if invalid_settings_path.exists():
                    invalid_settings_path.unlink()

import os
from pathlib import Path
from time import sleep
from unittest import TestCase, mock

from dandy.toolbox.utils import check_or_create_settings
import contextlib


INVALID_SETTINGS_MODULE_NAME = 'tests.invalid_dandy_settings'

BASE_PATH = Path(__file__).parent.parent.parent.resolve()


class TestUtils(TestCase):
    def test_check_or_create_settings(self):
        try:
            check_or_create_settings(cwd_path=BASE_PATH)
        except ImportError:
            self.fail('check_or_create_settings() raised ImportError unexpectedly!')

    def test_check_or_create_settings_invalid_settings_module_name(self):
        with mock.patch(
            'dandy.toolbox.utils.get_settings_module_name',
            return_value=INVALID_SETTINGS_MODULE_NAME,
        ), contextlib.suppress(ImportError):
            check_or_create_settings(
                cwd_path=BASE_PATH,
                system_exit_on_import_error=False,
            )

        with mock.patch(
            'dandy.toolbox.utils.get_settings_module_name',
            return_value=INVALID_SETTINGS_MODULE_NAME,
        ):
            try:
                check_or_create_settings(
                    cwd_path=BASE_PATH,
                )
            except ImportError:
                self.fail(
                    'check_or_create_settings() did not properly handle invalid settings module name!'
                )

            finally:
                settings_file_path_segments = INVALID_SETTINGS_MODULE_NAME.split('.')

                invalid_settings_path = (
                        BASE_PATH
                        / settings_file_path_segments[0]
                        / f"{settings_file_path_segments[1]}.py"
                )

                if invalid_settings_path.exists():
                    invalid_settings_path.unlink()

import contextlib
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from dandy.shared.constants import DANDY_LOCAL_DIRECTORY_NAME
from dandy.shared.settings.load import get_cli_llm_config
from dandy.interfaces.cli.utils import check_or_create_settings, ensure_dandy_gitignore
from dandy.shared.settings import settings

INVALID_SETTINGS_MODULE_NAME = 'tests.invalid_dandy_settings'

BASE_PATH = Path(__file__).parent.parent.parent.parent.resolve()


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
                'dandy.shared.settings.load.get_settings_module_name',
                return_value=INVALID_SETTINGS_MODULE_NAME,
            ),
            contextlib.suppress(ImportError),
        ):
            check_or_create_settings(cwd_path=BASE_PATH, system_exit_on_import_error=False)

        with mock.patch(
            'dandy.shared.settings.load.get_settings_module_name',
            return_value=INVALID_SETTINGS_MODULE_NAME,
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


class TestEnsureDandyGitignore(TestCase):
    GITIGNORE_PATTERN = f'{DANDY_LOCAL_DIRECTORY_NAME}/'
    APPENDED_TEXT = f'*.pyc\n{GITIGNORE_PATTERN}\n'

    def _make_project(
        self, project_path: Path, *, git: bool = True, gitignore: str | None = None
    ) -> Path:
        if git:
            (project_path / '.git').mkdir()

        if gitignore is not None:
            (project_path / '.gitignore').write_text(gitignore)

        return project_path

    def _gitignore_text(self, project_path: Path) -> str:
        return (project_path / '.gitignore').read_text()

    def test_non_git_project_is_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            project_path = self._make_project(Path(temp_name), git=False)

            ensure_dandy_gitignore(project_path)

            self.assertFalse((project_path / '.gitignore').exists())

    def test_git_project_without_gitignore_gets_one(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            project_path = self._make_project(Path(temp_name))

            ensure_dandy_gitignore(project_path)

            self.assertEqual(self._gitignore_text(project_path), f'{self.GITIGNORE_PATTERN}\n')

    def test_git_project_gitignore_gets_entry_appended(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            project_path = self._make_project(Path(temp_name), gitignore='*.pyc\n')

            ensure_dandy_gitignore(project_path)

            self.assertEqual(self._gitignore_text(project_path), self.APPENDED_TEXT)

    def test_git_project_gitignore_without_trailing_newline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            project_path = self._make_project(Path(temp_name), gitignore='*.pyc')

            ensure_dandy_gitignore(project_path)

            self.assertEqual(self._gitignore_text(project_path), self.APPENDED_TEXT)

    def test_existing_entry_leaves_gitignore_unchanged(self) -> None:
        original = f'node_modules/\n{self.GITIGNORE_PATTERN}\n'

        with tempfile.TemporaryDirectory() as temp_name:
            project_path = self._make_project(Path(temp_name), gitignore=original)

            ensure_dandy_gitignore(project_path)

            self.assertEqual(self._gitignore_text(project_path), original)

    def test_root_anchored_entry_is_recognized(self) -> None:
        original = '/.dandy/\n'

        with tempfile.TemporaryDirectory() as temp_name:
            project_path = self._make_project(Path(temp_name), gitignore=original)

            ensure_dandy_gitignore(project_path)

            self.assertEqual(self._gitignore_text(project_path), original)

    def test_call_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            project_path = self._make_project(Path(temp_name), gitignore='*.pyc\n')

            ensure_dandy_gitignore(project_path)
            ensure_dandy_gitignore(project_path)

            self.assertEqual(self._gitignore_text(project_path), self.APPENDED_TEXT)

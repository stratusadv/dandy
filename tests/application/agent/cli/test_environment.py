import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from dandy.application.agent.cli.environment import collect_environment, environment_section
from dandy.application.agent.session import session


def _init_git_repo(project_path: Path) -> None:
    git = [
        'git',
        '-c',
        'user.name=test',
        '-c',
        'user.email=test@example.com',
        '-c',
        'commit.gpgsign=false',
    ]
    subprocess.run([*git, 'init', '-q', '-b', 'test-branch'], cwd=project_path, check=True)
    subprocess.run([*git, 'add', '.'], cwd=project_path, check=True)
    subprocess.run([*git, 'commit', '-q', '-m', 'initial'], cwd=project_path, check=True)


class EnvironmentTestCase(TestCase):
    def setUp(self) -> None:
        self.temp_directory_context = TemporaryDirectory()
        self.project_path = Path(self.temp_directory_context.name)
        self.original_project_base_path = session.project_base_path
        session.project_base_path = self.project_path

    def tearDown(self) -> None:
        session.project_base_path = self.original_project_base_path
        self.temp_directory_context.cleanup()


class TestCollectEnvironment(EnvironmentTestCase):
    def test_collect_environment_without_git_repo(self) -> None:
        (self.project_path / 'src').mkdir()
        (self.project_path / '.venv').mkdir()
        (self.project_path / 'node_modules').mkdir()
        (self.project_path / 'main.py').touch()

        environment = collect_environment()

        self.assertIn('OS', environment)
        self.assertIn('Python', environment)
        self.assertIn('User', environment)
        self.assertIn(str(self.project_path), environment['Project root'])
        self.assertEqual(environment['Git'], 'not a git repository')
        self.assertIn('src/', environment['Top level'])
        self.assertIn('main.py', environment['Top level'])
        self.assertNotIn('.venv', environment['Top level'])
        self.assertNotIn('node_modules', environment['Top level'])

    def test_collect_environment_with_git_repo_and_changes(self) -> None:
        (self.project_path / 'main.py').write_text('print("hi")')
        _init_git_repo(self.project_path)
        (self.project_path / 'main.py').write_text('print("changed")')
        (self.project_path / 'new_file.py').touch()

        environment = collect_environment()

        self.assertIn('branch test-branch', environment['Git'])
        self.assertIn('changed', environment['Git'])

    def test_collect_environment_detects_build_tooling(self) -> None:
        (self.project_path / 'justfile').touch()

        environment = collect_environment()

        self.assertEqual(environment.get('Build tooling'), 'justfile')

    def test_collect_environment_tolerates_a_missing_project_root(self) -> None:
        missing_path = Path(self.project_path, 'gone')
        session.project_base_path = missing_path

        environment = collect_environment()

        self.assertEqual(environment['Top level'], 'unavailable')
        self.assertEqual(environment['Git'], 'not a git repository')


class TestEnvironmentSection(EnvironmentTestCase):
    def test_environment_section_renders_as_a_list(self) -> None:
        (self.project_path / 'main.py').touch()

        section_text = environment_section().to_str()

        self.assertIn('### Environment', section_text)
        self.assertIn('Project root:', section_text)
        self.assertIn('Git:', section_text)

    def test_environment_section_renders_even_when_git_fails(self) -> None:
        (self.project_path / '.git').mkdir()
        (self.project_path / 'main.py').touch()

        with mock.patch(
            'dandy.application.agent.cli.environment.subprocess.run',
            side_effect=OSError('git is broken'),
        ):
            section_text = environment_section().to_str()

        self.assertIn('### Environment', section_text)
        self.assertIn('not a git repository', section_text)

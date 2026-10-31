import tempfile
from pathlib import Path
from unittest import TestCase

from dandy.application.agent.session import DandyCliSession


class TestDandyCliSession(TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.project_base_path = Path(self._temp_dir.name)

    def tearDown(self) -> None:
        self._temp_dir.cleanup()

    def make_session(self) -> DandyCliSession:
        return DandyCliSession(project_base_path=self.project_base_path)

    def test_post_init_sets_project_base_path(self) -> None:
        session = DandyCliSession(project_base_path=Path(tempfile.gettempdir()))

        session.post_init(project_base_path=self.project_base_path)

        self.assertEqual(session.project_base_path, self.project_base_path)

    def test_derived_paths(self) -> None:
        session = self.make_session()

        self.assertEqual(session.project_dandy_path, self.project_base_path / '.dandy')
        self.assertEqual(session.project_dandy_cli_path, self.project_base_path / '.dandy' / 'cli')
        self.assertEqual(
            session.session_file_path, self.project_base_path / '.dandy' / 'cli' / 'session.json'
        )

    def test_load_without_session_file_stays_unloaded(self) -> None:
        session = self.make_session()

        session.load()

        self.assertFalse(session.is_loaded)
        self.assertFalse(session.session_file_path.is_file())

    def test_save_writes_session_file(self) -> None:
        session = self.make_session()

        session.save()

        self.assertTrue(session.session_file_path.is_file())
        self.assertTrue(session.is_loaded)

    def test_load_reads_saved_session_and_keeps_base_path(self) -> None:
        session = self.make_session()
        session.save()

        new_session = self.make_session()
        new_session.load()

        self.assertTrue(new_session.is_loaded)
        self.assertEqual(new_session.project_base_path, self.project_base_path)

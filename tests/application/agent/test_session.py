import tempfile
from pathlib import Path
from unittest import TestCase

from dandy.application.agent.session import DandyCliSession


class TestDandyCliSession(TestCase):
    def make_session(self, project_base_path: Path) -> DandyCliSession:
        return DandyCliSession(project_base_path=project_base_path)

    def test_project_base_path_is_reassignable(self) -> None:
        session = DandyCliSession(project_base_path=Path(tempfile.gettempdir()))
        project_base_path = Path('/some/project')

        session.project_base_path = project_base_path

        self.assertEqual(session.project_base_path, project_base_path)

    def test_derived_paths(self) -> None:
        project_base_path = Path('/some/project')
        session = self.make_session(project_base_path)

        self.assertEqual(session.project_dandy_path, project_base_path / '.dandy')
        self.assertEqual(session.agents_md_path, project_base_path / 'AGENTS.md')

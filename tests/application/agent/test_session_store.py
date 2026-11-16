import tempfile
from datetime import UTC, datetime
from pathlib import Path
from unittest import TestCase

from dandy.application.agent.exceptions import AgentUsageError, AgentExternalError
from dandy.application.agent.intel import AgentSession, SessionRecord
from dandy.application.agent.session_store import SessionStore
from dandy.domain.message.message import MessageHistory
from dandy.shared.files import write_to_file


def _make_session(request_text: str = 'Fix the login bug.') -> AgentSession:
    history = MessageHistory()
    history.add_message(role='system', text='You are helpful.')
    history.add_message(role='user', text=request_text)

    return AgentSession(messages=list(history.messages), last_request=request_text)


class TestSessionStore(TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.store = SessionStore(Path(self._temp_dir.name) / 'sessions')

    def tearDown(self) -> None:
        self._temp_dir.cleanup()

    def test_for_project_paths_sessions_under_project_dandy_dir(self) -> None:
        store = SessionStore.for_project(Path('/some/project'))

        self.assertEqual(store.sessions_path, Path('/some/project/.dandy/agent/sessions'))

    def test_save_and_load_round_trip(self) -> None:
        self.store.save('one', _make_session())

        session = self.store.load('one')

        self.assertEqual(session.last_request, 'Fix the login bug.')
        self.assertEqual([message.role for message in session.messages], ['system', 'user'])

    def test_save_keeps_created_at_and_bumps_updated_at(self) -> None:
        original_created_at = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
        existing = SessionRecord(
            name='one',
            created_at=original_created_at,
            updated_at=original_created_at,
            session=_make_session(),
        )
        write_to_file(self.store._record_path('one'), existing.model_dump_json())

        record = self.store.save('one', _make_session('Second request.'))

        self.assertEqual(record.created_at, original_created_at)
        self.assertGreater(record.updated_at, original_created_at)
        self.assertEqual(self.store.load('one').last_request, 'Second request.')

    def test_load_unknown_session_lists_available(self) -> None:
        self.store.save('one', _make_session())

        with self.assertRaises(AgentExternalError) as context:
            self.store.load('missing')

        self.assertIn('one', str(context.exception))

    def test_delete_removes_session_file(self) -> None:
        self.store.save('one', _make_session())

        self.store.delete('one')

        self.assertFalse(self.store._record_path('one').is_file())

    def test_delete_unknown_session_lists_available(self) -> None:
        self.store.save('one', _make_session())

        with self.assertRaises(AgentExternalError) as context:
            self.store.delete('missing')

        self.assertIn('one', str(context.exception))

    def test_latest_returns_most_recently_updated_name(self) -> None:
        self._write_record('older', updated_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC))
        self._write_record('newer', updated_at=datetime(2026, 1, 2, 0, 0, 0, tzinfo=UTC))

        self.assertEqual(self.store.latest(), 'newer')

    def test_latest_is_none_when_empty(self) -> None:
        self.assertIsNone(self.store.latest())

    def test_list_sessions_is_newest_first_and_skips_corrupted_files(self) -> None:
        self._write_record('older', updated_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC))
        self._write_record('newer', updated_at=datetime(2026, 1, 2, 0, 0, 0, tzinfo=UTC))
        write_to_file(self.store.sessions_path / 'broken.json', 'not json at all')

        names = [record.name for record in self.store.list_sessions()]

        self.assertEqual(names, ['newer', 'older'])

    def test_resolve_selection_empty_means_latest(self) -> None:
        self._write_record('one', updated_at=datetime(2026, 1, 2, 0, 0, 0, tzinfo=UTC))

        self.assertIsNone(self.store.resolve_selection(''))
        self.assertIsNone(self.store.resolve_selection('   '))

    def test_resolve_selection_number_picks_the_row_oldest_first(self) -> None:
        self._write_record('oldest', updated_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC))
        self._write_record('middle', updated_at=datetime(2026, 1, 2, 0, 0, 0, tzinfo=UTC))
        self._write_record('newest', updated_at=datetime(2026, 1, 3, 0, 0, 0, tzinfo=UTC))

        self.assertEqual(self.store.resolve_selection('1'), 'oldest')
        self.assertEqual(self.store.resolve_selection('2'), 'middle')
        self.assertEqual(self.store.resolve_selection('3'), 'newest')

    def test_resolve_selection_unknown_number_lists_available(self) -> None:
        self._write_record('oldest', updated_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC))
        self._write_record('newest', updated_at=datetime(2026, 1, 2, 0, 0, 0, tzinfo=UTC))

        for selection in ('0', '3', '99'):
            with self.assertRaises(AgentExternalError) as context:
                self.store.resolve_selection(selection)

            message = str(context.exception)
            self.assertIn(selection, message)
            self.assertIn('oldest', message)
            self.assertIn('newest', message)

    def test_resolve_selection_zero_is_not_a_row(self) -> None:
        self._write_record('0', updated_at=datetime(2026, 1, 2, 0, 0, 0, tzinfo=UTC))

        with self.assertRaises(AgentExternalError):
            self.store.resolve_selection('0')

    def test_resolve_selection_falls_back_to_exact_name(self) -> None:
        self._write_record('one', updated_at=datetime(2026, 1, 2, 0, 0, 0, tzinfo=UTC))

        self.assertEqual(self.store.resolve_selection('one'), 'one')

    def test_resolve_selection_unknown_name_lists_available(self) -> None:
        self._write_record('one', updated_at=datetime(2026, 1, 2, 0, 0, 0, tzinfo=UTC))

        with self.assertRaises(AgentExternalError) as context:
            self.store.resolve_selection('missing')

        self.assertIn('missing', str(context.exception))
        self.assertIn('one', str(context.exception))

    def test_new_name_slugifies_request_text(self) -> None:
        name = self.store.new_name('Fix the Login, Bug!')

        self.assertEqual(name, f'{datetime.now(UTC).strftime("%Y-%m-%d-%H-%M")}-fix-the-login-bug')

    def test_new_name_falls_back_for_empty_slug(self) -> None:
        name = self.store.new_name('!!!')

        self.assertEqual(name, f'{datetime.now(UTC).strftime("%Y-%m-%d-%H-%M")}-session')

    def test_new_name_avoids_collisions(self) -> None:
        base_name = self.store.new_name('Fix the login bug.')
        self.store.save(base_name, _make_session())

        second_name = self.store.new_name('Fix the login bug.')

        self.assertEqual(second_name, f'{base_name}-2')

    def test_save_rejects_path_traversal_names(self) -> None:
        for bad_name in ('', '.', '..', 'a/b', '../evil'):
            with self.assertRaises(AgentUsageError):
                self.store.save(bad_name, _make_session())

    def _write_record(self, name: str, updated_at: datetime) -> None:
        record = SessionRecord(
            name=name, created_at=updated_at, updated_at=updated_at, session=_make_session()
        )
        write_to_file(self.store._record_path(name), record.model_dump_json())

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from dandy.application.agent.exceptions import AgentCriticalError, AgentRecoverableError
from dandy.application.agent.intel import AgentSession, SessionRecord
from dandy.shared.constants import (
    AGENT_WORKING_DIRECTORY,
    DANDY_LOCAL_DIRECTORY_NAME,
    SESSIONS_DIRECTORY_NAME,
)
from dandy.shared.files import read_from_file, remove_file, write_to_file

SESSION_NAME_SLUG_CHARACTER_LIMIT = 40
SESSION_DATE_FORMAT = '%Y-%m-%d'


class SessionStore:
    """Reads, writes, and lists named agent sessions under a directory."""

    def __init__(self, sessions_path: Path) -> None:
        self.sessions_path = sessions_path

    @classmethod
    def for_project(cls, project_base_path: Path) -> SessionStore:
        return cls(
            sessions_path=Path(
                project_base_path,
                DANDY_LOCAL_DIRECTORY_NAME,
                AGENT_WORKING_DIRECTORY,
                SESSIONS_DIRECTORY_NAME,
            )
        )

    def save(self, name: str, session: AgentSession) -> SessionRecord:
        """Write a session under its name, keeping the original created time."""
        self._validate_name(name)
        record_path = self._record_path(name)
        now = datetime.now(UTC)
        record = SessionRecord(
            name=name,
            created_at=self._existing_created_at(record_path, now),
            updated_at=now,
            session=session,
        )

        write_to_file(record_path, record.model_dump_json(indent=2))

        return record

    def load(self, name: str) -> AgentSession:
        """Load the session stored under this exact name."""
        return self._load_record(name).session

    def delete(self, name: str) -> None:
        """Delete the session stored under this exact name."""
        record_path = self._record_path(name)

        if not record_path.is_file():
            self._raise_unknown_session(name)

        remove_file(record_path)

    def latest(self) -> str | None:
        """The name of the most recently updated session, or None when empty."""
        records = self.list_sessions()

        if not records:
            return None

        return max(records, key=lambda record: record.updated_at).name

    def list_sessions(self) -> list[SessionRecord]:
        """Every readable session record, newest first."""
        if not self.sessions_path.is_dir():
            return []

        records = []

        for record_path in self.sessions_path.glob('*.json'):
            try:
                records.append(SessionRecord.model_validate_json(read_from_file(record_path)))
            except (OSError, ValidationError):
                continue

        return sorted(records, key=lambda record: record.updated_at, reverse=True)

    def new_name(self, from_text: str) -> str:
        """A fresh non-colliding name derived from the first request text."""
        slug = _slugify(from_text)
        base_name = f'{datetime.now(UTC).strftime(SESSION_DATE_FORMAT)}-{slug or "session"}'
        candidate_name = base_name
        counter = 2

        while self._record_path(candidate_name).is_file():
            candidate_name = f'{base_name}-{counter}'
            counter += 1

        return candidate_name

    def _record_path(self, name: str) -> Path:
        return Path(self.sessions_path, f'{name}.json')

    def _load_record(self, name: str) -> SessionRecord:
        record_path = self._record_path(name)

        if not record_path.is_file():
            self._raise_unknown_session(name)

        try:
            return SessionRecord.model_validate_json(read_from_file(record_path))
        except (OSError, ValidationError):
            message = f'Session "{name}" could not be read from {record_path}.'
            raise AgentRecoverableError(message) from None

    def _existing_created_at(self, record_path: Path, fallback: datetime) -> datetime:
        if not record_path.is_file():
            return fallback

        try:
            return SessionRecord.model_validate_json(read_from_file(record_path)).created_at
        except (OSError, ValidationError):
            return fallback

    def _raise_unknown_session(self, name: str) -> None:
        available_names = [record.name for record in self.list_sessions()]
        available_str = ', '.join(available_names) if available_names else '(none)'

        message = f'Session "{name}" not found. Available sessions: {available_str}'
        raise AgentRecoverableError(message)

    @staticmethod
    def _validate_name(name: str) -> None:
        if not name or name in {'.', '..'} or '/' in name or '\\' in name:
            message = f'Invalid session name: "{name}"'
            raise AgentCriticalError(message)


def _slugify(text: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return slug[:SESSION_NAME_SLUG_CHARACTER_LIMIT].rstrip('-')

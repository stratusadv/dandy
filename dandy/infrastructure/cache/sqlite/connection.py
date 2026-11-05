import sqlite3
from pathlib import Path

from dandy.shared.settings import settings


class SqliteConnection:
    def __init__(self, db_name: str) -> None:
        self.db_path = Path(settings.CACHE_SQLITE_DATABASE_PATH, db_name)

    def __enter__(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.connection:
            self.connection.close()

    def delete_db_file(self) -> None:
        self.db_path.unlink()

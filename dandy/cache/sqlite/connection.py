import sqlite3
from pathlib import Path

from dandy.conf import settings


class SqliteConnection:
    def __init__(self, db_name: str):
        self.db_path = Path(settings.CACHE_SQLITE_DATABASE_PATH, db_name)

    def __enter__(self) -> sqlite3.Connection:
        self.connection = sqlite3.connect(self.db_path)
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()

    def delete_db_file(self):
        Path.unlink(self.db_path)

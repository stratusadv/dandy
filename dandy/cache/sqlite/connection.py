import sqlite3

from dandy.conf import settings

class SqliteConnection:
    def __enter__(self) -> sqlite3.Connection:
        self.connection = sqlite3.connect(settings.SQLITE_CACHE_DATABASE_PATH)
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()
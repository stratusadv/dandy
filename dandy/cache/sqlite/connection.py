import os
import sqlite3

from dandy.conf import settings


class SqliteConnection:
    def __init__(self) -> None:
        self.db_path = settings.CACHE_SQLITE_DATABASE_PATH

    def __enter__(self) -> sqlite3.Connection:
        self.connection = sqlite3.connect(self.db_path)
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()

    def delete_db_file(self):
        os.remove(self.db_path)
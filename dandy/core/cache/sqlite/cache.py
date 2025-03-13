import pickle
import sqlite3
from typing import Any, Union

import dandy.constants
from dandy.core.cache.cache import BaseCache
from dandy.core.cache.sqlite.connection import SqliteConnection
from dandy.constants import SQLITE_CACHE_TABLE_NAME


class SqliteCache(BaseCache):
    cache_name: str
    limit: int

    @property
    def db_name(self) -> str:
        return self._db_name(self.cache_name)

    @staticmethod
    def _db_name(cache_name: str) ->  str:
        return f"{cache_name}_cache.db"

    def model_post_init(self, __context: Any):
        self._create_table()

    def __len__(self) -> int:
        with SqliteConnection(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f'SELECT COUNT(*) FROM {SQLITE_CACHE_TABLE_NAME}')
            return cursor.fetchone()[0]

    def _create_table(self):
        with SqliteConnection(self.db_name) as connection:
            cursor = connection.cursor()

            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {SQLITE_CACHE_TABLE_NAME} (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            connection.commit()

    def get(self, key: str) -> Union[Any, None]:
        with SqliteConnection(self.db_name) as connection:
            cursor = connection.cursor()

            cursor.execute(f'SELECT value FROM {SQLITE_CACHE_TABLE_NAME} WHERE key = ?', (key,))
            result = cursor.fetchone()

            if result:
                return pickle.loads(result[0])

            return None

    def set(self, key: str, value: Any):
        with SqliteConnection(self.db_name) as connection:
            cursor = connection.cursor()

            value_string = pickle.dumps(value)

            try:
                cursor.execute(f'INSERT INTO {SQLITE_CACHE_TABLE_NAME} (key, value) VALUES (?, ?)', (key, value_string))
            except sqlite3.IntegrityError:
                cursor.execute(f'UPDATE {SQLITE_CACHE_TABLE_NAME} SET value = ? WHERE key = ?', (value_string, key))

            connection.commit()
            self.clean()

    def clean(self):
        with SqliteConnection(self.db_name) as connection:
            cursor = connection.cursor()

            cursor.execute(f'SELECT COUNT(*) FROM {SQLITE_CACHE_TABLE_NAME}')
            row_count = cursor.fetchone()[0]

            excess_threshold = int(self.limit * 0.10)
            excess_rows = row_count - self.limit

            if excess_rows >= excess_threshold:
                cursor.execute(
                    f'DELETE FROM {SQLITE_CACHE_TABLE_NAME} WHERE key IN (SELECT key FROM {SQLITE_CACHE_TABLE_NAME} ORDER BY created_at LIMIT ?)',
                    (excess_threshold,)
                )

            connection.commit()

    @classmethod
    def clear(cls, cache_name: str = dandy.constants.DEFAULT_CACHE_NAME):
        with SqliteConnection(cls._db_name(cache_name)) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{SQLITE_CACHE_TABLE_NAME}';")

            if cursor.fetchone() is not None:
                cursor.execute(f'DELETE FROM {SQLITE_CACHE_TABLE_NAME}')
                connection.commit()

    @classmethod
    def destroy(cls, cache_name: str = dandy.constants.DEFAULT_CACHE_NAME):
        SqliteConnection(cls._db_name(cache_name)).delete_db_file()

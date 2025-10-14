import pickle
import sqlite3
from typing import Any

import dandy.consts
from dandy.cache.cache import BaseCache
from dandy.cache.sqlite.connection import SqliteConnection
from dandy.consts import SQLITE_CACHE_TABLE_NAME, SQLITE_CACHE_DB_NAME


class SqliteCache(BaseCache):
    cache_name: str
    limit: int

    def model_post_init(self, __context: Any, /):
        self._create_table()

    def __len__(self) -> int:
        if not self._table_exists():
            return 0

        with SqliteConnection(SQLITE_CACHE_DB_NAME) as connection:
            cursor = connection.cursor()

            cursor.execute(
                f'SELECT COUNT(*) FROM {SQLITE_CACHE_TABLE_NAME} WHERE cache_name = ?',
                (self.cache_name,)
            )

            return cursor.fetchone()[0]

    @staticmethod
    def _table_exists() -> bool:
        with SqliteConnection(SQLITE_CACHE_DB_NAME) as connection:
            cursor = connection.cursor()

            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{SQLITE_CACHE_TABLE_NAME}';")

            return cursor.fetchone() is not None

    @staticmethod
    def _create_table():
        with SqliteConnection(SQLITE_CACHE_DB_NAME) as connection:
            cursor = connection.cursor()

            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {SQLITE_CACHE_TABLE_NAME} (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    cache_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            connection.commit()

    def get(self, key: str) -> Any | None:
        if not self._table_exists():
            return None

        with SqliteConnection(SQLITE_CACHE_DB_NAME) as connection:
            cursor = connection.cursor()

            cursor.execute(
                f'SELECT value FROM {SQLITE_CACHE_TABLE_NAME} WHERE key = ? AND cache_name = ?',
                (key, self.cache_name)
            )
            result = cursor.fetchone()

            if result:
                return pickle.loads(result[0])

            return None

    def set(self, key: str, value: Any):
        with SqliteConnection(SQLITE_CACHE_DB_NAME) as connection:
            cursor = connection.cursor()

            value_string = pickle.dumps(value)

            try:
                cursor.execute(
                    f'INSERT INTO {SQLITE_CACHE_TABLE_NAME} (key, value, cache_name) VALUES (?, ?, ?)',
                    (key, value_string, self.cache_name)
                )
            except sqlite3.IntegrityError:
                cursor.execute(
                    f'UPDATE {SQLITE_CACHE_TABLE_NAME} SET value = ? WHERE key = ? AND cache_name = ?',
                    (value_string, key, self.cache_name)
                )

            connection.commit()
            self.clean()

    def clean(self):
        with SqliteConnection(SQLITE_CACHE_DB_NAME) as connection:
            cursor = connection.cursor()

            excess_threshold = int(self.limit * 0.10)
            excess_rows = self.__len__() - self.limit

            if excess_rows >= excess_threshold:
                cursor.execute(
                    f'DELETE FROM {SQLITE_CACHE_TABLE_NAME} WHERE key IN (SELECT key FROM {SQLITE_CACHE_TABLE_NAME} WHERE cache_name = ? ORDER BY created_at LIMIT ?)',
                    (self.cache_name, excess_threshold)
                )

            connection.commit()

    @classmethod
    def clear(cls, cache_name: str = dandy.consts.CACHE_DEFAULT_NAME):
        if cls._table_exists():
            with SqliteConnection(SQLITE_CACHE_DB_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    f'DELETE FROM {SQLITE_CACHE_TABLE_NAME} WHERE cache_name = ?',
                    (cache_name,)
                )
                connection.commit()

    @classmethod
    def clear_all(cls):
        if cls._table_exists():
            with SqliteConnection(SQLITE_CACHE_DB_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute(f'DELETE FROM {SQLITE_CACHE_TABLE_NAME}')
                connection.commit()

    @classmethod
    def destroy_all(cls):
        SqliteConnection(SQLITE_CACHE_DB_NAME).delete_db_file()

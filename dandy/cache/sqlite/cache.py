import pickle
import sqlite3
from typing import Any, Union

from dandy.cache.cache import BaseCache
from dandy.cache.sqlite.connection import SqliteConnection
from dandy.conf import settings 



class SqliteCache(BaseCache):
    limit: int = 1000
    
    def model_post_init(self, __context: Any):
        self._create_table()

    @staticmethod
    def _create_table():
        with SqliteConnection() as connection:
            cursor = connection.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            connection.commit()

    def get(self, key: str) -> Union[Any, None]:
        with SqliteConnection() as connection:
            cursor = connection.cursor()
            
            cursor.execute('SELECT value FROM cache WHERE key = ?', (key,))
            result = cursor.fetchone()
            
            if result:
                return pickle.loads(result[0])
            
            return None

    def set(self, key: str, value: Any):
        with SqliteConnection() as connection:
            cursor = connection.cursor()
            
            value_string = pickle.dumps(value)
            
            try:
                cursor.execute('INSERT INTO cache (key, value) VALUES (?, ?)', (key, value_string))
            except sqlite3.IntegrityError:
                cursor.execute('UPDATE cache SET value = ? WHERE key = ?', (value_string, key))
            
            connection.commit()
            self.clean()

    def clean(self):
        with SqliteConnection() as connection:
            cursor = connection.cursor()

            cursor.execute('SELECT COUNT(*) FROM cache')
            row_count = cursor.fetchone()[0]

            excess_threshold = self.limit * 0.05
            excess_rows = row_count - self.limit

            if excess_rows >= excess_threshold:
                cursor.execute('DELETE FROM cache ORDER BY created_at ASC LIMIT ?', (excess_threshold,))

            connection.commit()

    def clear(self):
        with SqliteConnection() as connection:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM cache')
            connection.commit()

    
    
sqlite_cache = SqliteCache()
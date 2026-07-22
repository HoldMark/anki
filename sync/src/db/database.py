import sqlite3
import textwrap
from sqlite3 import Connection

from src.utils.logging import get_logger

logger = get_logger(__name__)


class Database:
    def __init__(self, name):
        self._NAME = name
        self._connection: Connection | None = None

    def connection(self) -> Connection:
        """Creates and returns a connection to the database"""

        if not self._connection:
            self._connection = sqlite3.connect(self._NAME)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON;")

        return self._connection

    def close(self):
        """Closes the connection to the database"""

        if self._connection:
            self._connection.close()
            self._connection = None

    def __del__(self):
        """Destructor method that closes the connection to the database"""
        self.close()

    def execute(self, sql: str, params: dict | tuple = ()) -> int | None:
        """
        Метод для изменения данных в БД. Для таких запросов как INSERT, UPDATE, DELETE, CREATE TABLE, DROP TABLE и т.д.
        1. фиксирует изменения (conn.commit())
        2. не возвращает данных
        3. для команд, где важен побочный эффект, а не результат чтения
        """
        conn = self.connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            if sql.strip().startswith("INSERT"):
                return cursor.lastrowid
        except Exception:
            logger.error("Got error while changing data in the database", exc_info=True)
            return None
        else:
            return 1
        finally:
            cursor.close()

    def query(self, sql: str, params=()) -> list[dict] | None:
        """
        Метод для чтения данных из БД.
        1. не фиксирует изменений
        2. возвращает данные
        3. преобразует данные в список словарей
        """
        conn = self.connection()
        cursor = conn.cursor()

        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception:
            logger.error("Got error while reading data from the database", exc_info=True)
            return None

        finally:
            cursor.close()

    def table_names(self) -> set[str] | None:
        """Returns a set of table names"""
        query = textwrap.dedent("""
            SELECT name
            FROM sqlite_master
            WHERE type='table';
        """)

        created_tables = self.query(query)
        return {i["name"] for i in created_tables} if created_tables is not None else None

    def are_tables_created(self, tables) -> bool | None:
        """Checks if all tables are created"""

        created_table_names = self.table_names()
        expected_table_names = {table.NAME for table in tables}

        if created_table_names is None:
            return None

        if created_table_names.issuperset(expected_table_names):
            return True

        return False

    def create_tables(self, tables) -> bool | None:
        """Creates tables if they are not created"""

        are_created = self.are_tables_created(tables)

        if are_created is None:
            return None

        if not are_created:
            counter = 0

            for table in tables:
                counter += 1 if table.create() else 0

            if counter == len(tables):
                return True

            return None

        return True

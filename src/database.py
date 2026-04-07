import re
import sqlite3


def _validate_identifier(name):
    """Raise ValueError if name is not a safe SQL identifier (alphanumeric + underscore)."""
    if not re.match(r'^\w+$', name):
        raise ValueError(f"Invalid SQL identifier: {name!r}")
    return name


class SQLiteDB:
    """SQLite wrapper. Assumes each row contains one column: encrypted_text."""

    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def create_table(self, table_name, table_spec='encrypted_text TEXT'):
        cursor = self.connection.cursor()
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {_validate_identifier(table_name)} ({table_spec})"
        )
        self.connection.commit()
        cursor.close()

    def select_all(self, table_name):
        cursor = self.connection.cursor()
        res = cursor.execute(
            f"SELECT * FROM {_validate_identifier(table_name)}"
        ).fetchall()
        cursor.close()
        return [r[0] for r in res]

    def add(self, table_name, data):
        cursor = self.connection.cursor()
        cursor.execute(
            f"INSERT INTO {_validate_identifier(table_name)} VALUES (?)",
            (data,)
        )
        self.connection.commit()
        cursor.close()

    def update(self, table_name, data):
        pass  # Not yet implemented


class FileDB:
    def __init__(self, file):
        self.file = file

    def save_to_file(self, msg):
        if isinstance(msg, list):
            msg = '\n'.join(msg)
        with open(self.file, 'w') as f:
            f.write(msg)

    def load_file(self):
        with open(self.file, 'r') as f:
            return [line.rstrip('\n') for line in f]

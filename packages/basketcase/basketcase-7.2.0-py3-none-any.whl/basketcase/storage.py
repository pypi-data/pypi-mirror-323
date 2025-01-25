import sqlite3

from .models import Session


def dataclass_factory(cursor, row):
    return Session(
        rowid=row[0],
        description=row[1],
        cookie_id=row[2],
        is_default=row[3],
        first_used=row[4]
    )


class Storage:
    """Database handler for internal program data"""

    def __init__(self, base_dir: str):
        self.connection = sqlite3.connect(f'{base_dir}/data.db')
        self.connection.row_factory = dataclass_factory
        self.initialize()

    def initialize(self):
        cursor = self.connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session (
                description TEXT,
                cookie_id TEXT,
                is_default INTEGER,
                first_used TEXT
            )
        ''')

        self.connection.commit()

    def get_one_by_id(self, rowid: int) -> Session | None:
        cursor = self.connection.cursor()

        cursor.execute('''
            SELECT rowid, * FROM session
            WHERE rowid = :rowid
        ''', {
            'rowid': rowid
        })

        session = cursor.fetchone()

        if not session:
            return None

        return session

    def get_all(self) -> list[Session]:
        cursor = self.connection.cursor()

        cursor.execute('''
            SELECT rowid, * FROM session
        ''')

        return cursor.fetchall()

    def update(self, session: Session):
        cursor = self.connection.cursor()

        cursor.execute('''
            UPDATE session SET
                description = :description,
                cookie_id = :cookie_id,
                is_default = :is_default
            WHERE rowid = :rowid
        ''', {
            'rowid': session.rowid,
            'description': session.description,
            'cookie_id': session.cookie_id,
            'is_default': session.is_default
        })

        self.connection.commit()

    def insert(self, session: Session) -> int:
        cursor = self.connection.cursor()

        cursor.execute('''
            INSERT INTO session (
                description,
                cookie_id,
                is_default,
                first_used
            ) VALUES (
                :description,
                :cookie_id,
                :is_default,
                datetime()
            )
        ''', {
            'description': session.description,
            'cookie_id': session.cookie_id,
            'is_default': session.is_default
        })

        self.connection.commit()

        return cursor.lastrowid

    def reset_default(self):
        cursor = self.connection.cursor()

        cursor.execute('''
            UPDATE session SET
                is_default = 0
        ''')

        self.connection.commit()

    def delete(self, session: Session):
        cursor = self.connection.cursor()

        cursor.execute('''
            DELETE FROM session
            WHERE rowid = :rowid
        ''', {
            'rowid': session.rowid
        })

        self.connection.commit()

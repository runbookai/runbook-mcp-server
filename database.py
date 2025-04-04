import os
import sys
import sqlite3
import logging
import time
import yaml
from pathlib import Path

log = logging.getLogger("foo")

class Config(object):

    def __init__(self, config_file_path: str):
        with open(config_file_path, 'r') as f:
            config = yaml.safe_load(f)
            self.__database_uri = config['database']['uri']
            self.__migration_dir = config['database']['migrationDir']

    @property
    def database_uri(self) -> str:
        return self.__database_uri

    @property
    def migration_dir(self) -> str:
        return self.__migration_dir

class Runbook(object):

    def __init__(self, external_id: str, name: str, content: str):
        self.__external_id = external_id
        self.__name = name
        self.__content = content

    @property
    def external_id(self) -> str:
        return self.__external_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def content(self) -> str:
        return self.__content

    def to_json(self):
        return {
            "external_id": self.__external_id,
            "name": self.__name,
            "content": self.__content
        }

class Store(object):

    def __init__(self, database_uri: str):
        self.__database_uri = database_uri

        self.__con = sqlite3.connect(self.__database_uri)
        self.__cursor = self.__con.cursor()

    def run_migrations(self, migrations_dir: str):
        """Run the scheme migrations.

        Follow https://eskerda.com/sqlite-schema-migrations-python/.
        Each migration starts setting PRAGMA user_version to a number.

        """
        # Find all files under the migrations directory
        migrations = sorted(Path(migrations_dir).glob("*.sql"))

        conn = sqlite3.connect(self.__database_uri)
        current_version, = next(conn.cursor().execute('PRAGMA user_version'), (0, ))

        for migration in migrations[current_version:]:
            cur = conn.cursor()
            try:
                log.info("Applying %s", migration.name)
                cur.executescript("BEGIN;" + migration.read_text())
            except Exception as e:
                log.error("Failed migration %s: %s. Bye", migration.name, e)
                cur.execute("ROLLBACK")
                sys.exit(1)
            else:
                cur.execute("COMMIT")

    def create_runbook(self, runbook):
        self.__cursor.execute(f"""
INSERT INTO runbooks (
  external_id,
  name,
  content
) VALUES (
  '{runbook.external_id}',
  '{runbook.name}',
  '{runbook.content}')
""")
        self.__con.commit()

    def get_runbook_by_external_id(self, external_id: str) -> Runbook:
        res = self.__cursor.execute(f"SELECT external_id, name, content FROM runbooks WHERE external_id = '{external_id}'")
        row = res.fetchone()
        if not row:
            raise Exception('not found')
        external_id = row[0]
        name = row[1]
        content = row[2]
        return Runbook(external_id, name, content)

    def get_runbook_by_name(self, name: str) -> Runbook:
        res = self.__cursor.execute(f"SELECT external_id, name, content FROM runbooks WHERE name = '{name}'")
        row = res.fetchone()
        if not row:
            raise Exception('not found')
        external_id = row[0]
        name = row[1]
        content = row[2]
        return Runbook(external_id, name, content)

    def delete_runbook_by_name(self, name: str) -> Runbook:
        self.__cursor.execute(f"DELETE FROM runbooks WHERE name = '{name}'")
        self.__con.commit()

    def list_runbooks(self) -> list[Runbook]:
        res = self.__cursor.execute("SELECT external_id, name, content FROM runbooks")
        rs = []
        for row in res:
            print(row)
            external_id = row[0]
            name = row[1]
            content = row[2]
            rs.append(Runbook(external_id, name, content))
        return rs

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
            d = config['database']
            self.__database_uri = d['uri']
            self.__migration_dir = d['migrationDir']
            self.__runbook_file_dir = os.path.abspath(d['runbookFileDir'])
            self.__runbook_log_dir = os.path.abspath(d['runbookLogDir'])

    @property
    def database_uri(self) -> str:
        return self.__database_uri

    @property
    def migration_dir(self) -> str:
        return self.__migration_dir

    @property
    def runbook_file_dir(self) -> str:
        return self.__runbook_file_dir

    @property
    def runbook_log_dir(self) -> str:
        return self.__runbook_log_dir


class Runbook(object):

    def __init__(self, external_id: str, name: str, file_path: str):
        self.__external_id = external_id
        self.__name = name
        self.__file_path = file_path

    @property
    def external_id(self) -> str:
        return self.__external_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def file_path(self) -> str:
        return self.__file_path

    def to_json(self):
        return {
            "external_id": self.__external_id,
            "name": self.__name,
            "content": self.__file_path
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
  file_path
) VALUES (
  '{runbook.external_id}',
  '{runbook.name}',
  '{runbook.file_path}')
""")
        self.__con.commit()

    def get_runbook_by_external_id(self, external_id: str) -> Runbook:
        res = self.__cursor.execute(f"SELECT external_id, name, file_path FROM runbooks WHERE external_id = '{external_id}'")
        row = res.fetchone()
        if not row:
            raise Exception(f"Runbook of external ID '%{external_id} not found")
        external_id = row[0]
        name = row[1]
        file_path = row[2]
        return Runbook(external_id, name, file_path)

    def get_runbook_by_name(self, name: str) -> Runbook:
        res = self.__cursor.execute(f"SELECT external_id, name, file_path FROM runbooks WHERE name = '{name}'")
        row = res.fetchone()
        if not row:
            raise Exception(f"Runbook of name '%{name} not found")
        external_id = row[0]
        name = row[1]
        file_path = row[2]
        return Runbook(external_id, name, file_path)

    def delete_runbook_by_name(self, name: str) -> Runbook:
        self.__cursor.execute(f"DELETE FROM runbooks WHERE name = '{name}'")
        self.__con.commit()

    def list_runbooks(self) -> list[Runbook]:
        res = self.__cursor.execute("SELECT external_id, name, file_path FROM runbooks")
        rs = []
        for row in res:
            print(row)
            external_id = row[0]
            name = row[1]
            file_path = row[2]
            rs.append(Runbook(external_id, name, file_path))
        return rs

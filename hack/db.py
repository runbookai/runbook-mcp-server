import sqlite3

class Config(object):

    def __init__(self, sqlite_filename):
        self.__sqlite_filename = sqlite_filename

    @property
    def sqlite_filename(self):
        return self.__sqlite_filename


class Runbook(object):

    def __init__(self, runbook_id, name, content):
        self.__runbook_id = runbook_id
        self.__name = name
        self.__content = content
        self.__org_id = ''
        self.__project_id = ''

    @property
    def runbook_id(self):
        return self.__runbook_id

    @property
    def name(self):
        return self.__name

    @property
    def content(self):
        return self.__content

    def __str__(self):
        return '(%s,%s,%s)' % (self.__runbook_id, self.__name, self.__content)


class Store(object):

    def __init__(self, dbname):
        self.__con = sqlite3.connect(dbname)
        self.__cursor = self.__con.cursor()

    def run_migration(self):
        # TODO(kenji): Set unique constraint violation
        self.__cursor.execute("CREATE TABLE runbooks(runbook_id, name, org_id, project_id, content)")

    def create_runbook(self, runbook):
        self.__cursor.execute("""
INSERT INTO
  runbooks (runbook_id, name, org_id, project_id, content)
VALUES ('%s', '%s', '', '', '%s')
""" % (runbook.runbook_id, runbook.name, runbook.content))
        self.__con.commit()


    def get_runbook_by_id(self, runbook_id):
        res = self.__cursor.execute("SELECT runbook_id, name, content FROM runbooks WHERE runbook_id = '%s'" % (runbook_id))
        row = res.fetchone()
        if not row:
            raise Exception('not found')
        runbook_id = row[0]
        name = row[1]
        content = row[2]

    def list_runbooks(self):
        res = self.__cursor.execute("SELECT runbook_id, name, content FROM runbooks")
        rs = []
        for row in res:
            print(row)
            runbook_id = row[0]
            name = row[1]
            content = row[2]
            rs.append(Runbook(runbook_id, name, content))
        return rs


conf = Config('runbooks.db')

s = Store(conf.sqlite_filename)

s.run_migration()

r = Runbook('r01', 'my-runbook', 'content')
s.create_runbook(r)

got = s.list_runbooks()
print(got[0])

got = s.get_runbook_by_id('r01')
print(got)

from connections.base_connection import BaseConnection
from impala.dbapi import connect
import os
class ImpalaConnection(BaseConnection):
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.__enter__()

    def __enter__(self):
        use_ssl = os.environ['DCHK_ENV'] == 'production'
        kwargs = {
            'host': self.host, 
            'port': self.port, 
            'user': self.user, 
            'password': self.password
        }

        if(os.environ['DCHK_ENV'] == 'production'):
            kwargs['use_ssl'] = True
            kwargs['auth_mechanism'] = 'PLAIN'

        self.db = connect(**kwargs)
        
        return self

    def __exit__(self, type, value, traceback):
        self.db.close()


    def close(self):
        self.db.close()


    def cursor(self):
        return self.db.cursor()


    def commit(self):
        return self.db.commit()


    def tables(self, schemas):
        tables = []
        cur = self.cursor()

        for sch in schemas:
            cur.execute("use %s" % (sch))
            cur.execute("show tables")
            tables = tables + map(lambda r: "{}.{}".format(sch, r[0]), cur.fetchall())


        return list(set(tables))


    def columns(self, table):
        cur = self.cursor()

        cur.execute("SHOW COLUMN STATS {}".format(table))

        return [row[0] for row in cur]


    def col_present(self, table, column):
        cur = self.cursor()

        cur.execute("SHOW COLUMN STATS {}".format(table))

        for row in cur:
            if row[0] == column:
                return True 

        return False


    def count(self, table):
        cur = self.cursor()

        cur.execute("select count(*) from {}".format(table))

        return cur.fetchone()[0]
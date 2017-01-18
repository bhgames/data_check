from connections.base_connection import BaseConnection
from psycopg2 import connect
import os
class PostgresConnection(BaseConnection):
    def __enter__(self):
        kwargs = {
            'host': self.host, 
            'port': self.port, 
            'user': self.user, 
            'dbname': self.dbname,
            'password': self.password
        }

        if(os.environ['DCHK_ENV'] == 'production'):
            kwargs['sslmode'] = True

        self.db = connect(**kwargs)
        
        return self



    def tables(self, schemas):
        tables = []
        cur = self.cursor()

        for sch in schemas:
            cur.execute("select tablename from pg_tables where schemaname='%s'" % (sch))
            tables = tables + map(lambda r: "{}.{}".format(sch, r[0]), cur.fetchall())

        return list(set(tables))


    def columns(self, table):
        cur = self.cursor()
        table_and_schema = table.split(".")
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = '{}'
              AND table_name   = '{}'
        """.format(*table_and_schema))

        return [row[0] for row in cur.fetchall()]


    def col_present(self, table, column):
        cur = self.cursor()
        table_and_schema = table.split(".")

        cur.execute("""
            SELECT EXISTS(
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = '{}'
                  AND table_name   = '{}'
                  AND column_name = '{}'
                );
        """.format(table_and_schema[0], table_and_schema[1], column))

        return cur.fetchone()
class BaseConnection:
    def __init__(self, **kwargs):
        self.host = kwargs['host']
        self.port = int(kwargs['port'])
        self.user = kwargs['user']
        self.password = kwargs['password']
        self.dbname = kwargs['dbname']
        self.data_source_type = kwargs['data_source_type']
        self.__enter__()

    def __exit__(self, type, value, traceback):
        self.db.close()


    def close(self):
        self.db.close()


    def cursor(self):
        return self.db.cursor()


    def commit(self):
        return self.db.commit()


    def count(self, table):
        cur = self.cursor()

        cur.execute("select count(*) from {}".format(table))

        return cur.fetchone()[0]
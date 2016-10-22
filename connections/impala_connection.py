from connections.base_connection import BaseConnection
from impala.dbapi import connect
class ImpalaConnection(BaseConnection):
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.__enter__()

    def __enter__(self):
        self.db = connect(host=self.host, port=self.port, user=self.user, password=self.password)
        return self.db

    def __exit__(self, type, value, traceback):
        self.db.close()

    def close(self):
        self.db.close()

    def cursor(self):
        return self.db.cursor()
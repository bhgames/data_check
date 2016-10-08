from base_connection import BaseConnection
from impala.dbapi import connect
class ImpalaConnection(BaseConnection):
    def __enter__(self, host, port):
        self.db = connect(host=host, port=port)
        return self.db

    def __exit__(self):
        self.db.close()
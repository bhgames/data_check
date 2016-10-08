from connections.base_connection import BaseConnection
from impala.dbapi import connect
class ImpalaConnection(BaseConnection):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __enter__(self):
        self.db = connect(host=self.host, port=self.port)
        return self.db

    def __exit__(self, type, value, traceback):
        self.db.close()
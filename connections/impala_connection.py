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
        
        return self.db

    def __exit__(self, type, value, traceback):
        self.db.close()

    def close(self):
        self.db.close()

    def cursor(self):
        return self.db.cursor()

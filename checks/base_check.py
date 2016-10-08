from connections.impala_connection import ImpalaConnection
import pandas as pd
from impala.util import as_pandas
import pandas as pd

class BaseCheck:
    def __init__(self, opts = {}):
        self.table = opts["table"]
        self.schema = opts["schema"]
        self.column = opts["column"]
        self.config = opts["config"]
        self.query_settings = { 'table': self.table, 'col': self.column, 'schema': self.schema }


    def run(self):
        with ImpalaConnection(self.config["host"], self.config["port"]) as db:
            self.inner_run(db)
            self.run_failed_rows_query(db)


    def inner_run(db):
        raise ValueError('Implement me!')


    def run_failed_rows_query(self, db):
        cur = db.cursor()

        if self.failed:
            cur.execute(self.failed_rows_query)

            self.failed_rows = as_pandas(cur)
        else:
            self.failed_rows = pd.DataFrame()
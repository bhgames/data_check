from connections.impala_connection import ImpalaConnection
import pandas as pd
from impala.util import as_pandas
import pandas as pd

class BaseCheck:
    def __init__(self, opts = {}):
        self.table = opts["table"]
        self.schema = opts["schema"]
        self.column = opts["column"] if "column" in opts else None
        self.expression = opts["expression"] if "expression" in opts else None
        self.threshold = opts["threshold"] if "threshold" in opts else None
        self.config = opts["config"]
        self.log_metadata = opts["log_metadata"] if "log_metadata" in opts else {}
        self.log = opts["log"] if "log" in opts else None
        self.query_settings = { 'table': self.table, 'col': self.column, 'threshold': self.threshold, 'schema': self.schema, 'expression': self.expression }


    def add_log(self, event, message):
        if self.log:
            self.log.add_log(event, message, self.log_metadata)


    def add_results_csv_to_s3(self):
        """
            Big TODO here
        """
        pass


    def run(self):
        with ImpalaConnection(self.config["host"], self.config["port"], self.config["user"], self.config["password"]) as db:
            self.inner_run(db)
            if self.failed:
                self.add_log("check_failed", "Check fails")
            else:
                self.add_log("check_succeeded", "Check succeeds")
            self.run_failed_rows_query(db)
            self.add_results_csv_to_s3()


    def inner_run(db):
        raise ValueError('Implement me!')


    def run_failed_rows_query(self, db):
        cur = db.cursor()

        if self.failed:
            self.add_log("collection", "Collect failed rows with query %s" % self.failed_rows_query)

            cur.execute(self.failed_rows_query)

            self.failed_rows = as_pandas(cur)

            self.add_log("result", "Failed Row Result Count: %s" % (len(self.failed_rows)))
        else:
            self.failed_rows = pd.DataFrame()

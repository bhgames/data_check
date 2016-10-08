
from checks.base_check import BaseCheck
from connections.impala_connection import ImpalaConnection
from impala.util import as_pandas

class UniquenessCheck(BaseCheck):
    def __init__(self, opts = {}):
        self.table = opts["table"]
        self.column = opts["column"]
        self.config = opts["config"]

    def run():
        with ImpalaConnection(self.config["host"], self.config["port"]) as db:
            cur = db.cursor()

            cur.execute("""
                select count(%(col)s) as count, count(distinct %(col)s) as dist_count from %(table)s
            """ % { 'table': self.table, 'col': self.col })

            result = as_pandas(cur)

            self.failed_rows = result[result.count != result.dist_count]

            self.failed = len(self.failed_rows > 0)
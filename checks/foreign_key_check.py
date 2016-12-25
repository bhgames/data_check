
from checks.base_check import BaseCheck
import re

class ForeignKeyCheck(BaseCheck):
    def __init__(self, opts = {}):
        super(ForeignKeyCheck, self).__init__(opts)
        self.query_settings["fk_col_pattern"] = opts["fk_col_pattern"]
        self.query_settings["fk_table_id_pattern"] = opts["fk_table_id_pattern"]


    def inner_run(self, db):
        cur = db.cursor()

        fk_col_pattern = re.compile(self.query_settings["fk_col_pattern"])
        fk_table_id_pattern = re.compile(self.query_settings["fk_table_id_pattern"])

        col_matching = filter(lambda col: re.search(fk_col_pattern, col), db.columns("{}.{}".format(self.schema, self.table)))

        failed_row_unions = []

        if len(col_matching) == 0:
            self.add_log("warning", "No columns matching {} found on table {}".format(self.query_settings["fk_col_pattern"], self.table))
            return

        for col in col_matching:
            fk_table = None

            try:
                fk_table = re.match(fk_col_pattern, col).group(1) # Grab first capture
            except IndexError, e:
                self.add_log("warning", "Check on {}'s column {} failed due to fk_col_pattern {} not containing any capture group for the FK table name".format(self.table, col, self.query_settings["fk_col_pattern"]))
                self.failed = True
                continue

            fk_table_id = filter(lambda col: re.search(fk_table_id_pattern, col), db.columns("{}.{}".format(self.schema, fk_table)))

            if len(fk_table_id) == 0:
                self.add_log(
                    "warning", 
                    "Check on {}'s column {} failed due to table fk_table_id_pattern {} not matching against any column on {}".format(self.table, col, self.query_settings["fk_table_id_pattern"], fk_table)
                )
                self.failed = True
                continue

            fk_table_id = fk_table_id[0]

            self.query_settings["fk_table_id"] = fk_table_id
            self.query_settings["fk_table"] = fk_table
            self.query_settings["col"] = col

            subquery = """
                %(schema)s.%(table)s left anti join %(schema)s.%(fk_table)s on %(table)s.%(col)s = %(fk_table)s.%(fk_table_id)s where %(table)s.%(col)s is not null
            """ % self.query_settings

            query = "select count(*) from " + subquery
            failed_row_unions.append("select * from {}".format(subquery))

            self.add_log("collection", "Run query %s" % (query))
        
            cur.execute(query)

            row = cur.fetchone()

            self.add_log("result", "Query came back with count %s" %(row[0]))

            # This way self.failed never gets set to false once true, can only go one direction.
            fail = row[0] > 0

            if fail:
                self.failed = True
        
        if len(failed_row_unions) > 0:
            self.failed_rows_query = """
                    select  * from ({}) t
                """.format(" union ".join(failed_row_unions))

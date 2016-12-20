
from checks.base_check import BaseCheck

class ColumnComparisonCheck(BaseCheck):

    def inner_run(self, db):
        cur = db.cursor()

        query = """
            select count(*) from (select %(expression)s as condition from `%(schema)s`.`%(table)s`) t where t.condition = false
        """ % self.query_settings

        self.add_log("collection", "Run query %s" % (query))
        
        cur.execute(query)

        row = cur.fetchone()

        self.add_log("result", "Query came back with count %s" %(row[0]))

        self.failed = row[0] > 0

        self.failed_rows_query = """
                select * from (select *, %(expression)s as condition from `%(schema)s`.`%(table)s`) t where t.condition = false limit 10000
            """ % self.query_settings


from checks.base_check import BaseCheck


class NullCheck(BaseCheck):

    def inner_run(self, db):
        cur = db.cursor()
        query = """
            select count(*) from `%(schema)s`.`%(table)s` where `%(col)s` is null
        """ % self.query_settings

        self.add_log("collection", "Run query %s" % (query))

        cur.execute(query)

        row = cur.fetchone()

        self.add_log("result", "Query came back with count %s" %(row[0]))

        self.failed = row[0] > 0

        self.failed_rows_query = """
                select * from `%(schema)s`.`%(table)s` where `%(col)s` is null
            """ % self.query_settings
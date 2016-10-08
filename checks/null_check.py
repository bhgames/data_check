
from checks.base_check import BaseCheck


class NullCheck(BaseCheck):

    def inner_run(self, db):
        cur = db.cursor()

        cur.execute("""
            select count(*) from `%(schema)s`.`%(table)s` where `%(col)s` is null
        """ % self.query_settings)

        row = cur.fetchone()

        self.failed = row[0] > 0

        self.failed_rows_query = """
                select * from `%(schema)s`.`%(table)s` where `%(col)s` is null
            """ % self.query_settings
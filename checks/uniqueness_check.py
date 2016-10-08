
from checks.base_check import BaseCheck
from connections.impala_connection import ImpalaConnection


class UniquenessCheck(BaseCheck):

    def inner_run(self, db):
        cur = db.cursor()

        cur.execute("""
            select count(`%(col)s`) as count, count(distinct `%(col)s`) as dist_count from `%(schema)s`.`%(table)s`
        """ % self.query_settings)

        row = cur.fetchone()

        self.failed = row[0] != row[1]

        self.failed_rows_query = """
                select `%(col)s` from (select `%(col)s`, count(*) as count from `%(schema)s`.`%(table)s` group by `%(col)s`) t where count > 1
            """ % self.query_settings
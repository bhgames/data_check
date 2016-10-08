
from checks.base_check import BaseCheck

class DateGapCheck(BaseCheck):

    def inner_run(self, db):
        cur = db.cursor()

        cur.execute("""
            select count(*) from (select abs(datediff(lag(`%(col)s`, 1) over (order by `%(col)s`), `%(col)s`)) as diff, `%(col)s` from `%(schema)s`.`%(table)s`) t where diff > 1
        """ % self.query_settings)

        row = cur.fetchone()

        self.failed = row[0] > 0

        self.failed_rows_query = """
                select gap_start, gap_end from (
                    select `%(col)s` as gap_start, lead(`%(col)s`,1) over (order by `%(col)s`) as gap_end from 
                        (
                            select abs(datediff(lag(`%(col)s`, 1) over (order by `%(col)s`), `%(col)s`)) as diff, `%(col)s` from `%(schema)s`.`%(table)s`) t where diff > 1
                        ) t2
                    where gap_end is not null
            """ % self.query_settings
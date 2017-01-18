
from checks.base_check import BaseCheck

class DateGapCheck(BaseCheck):

    @classmethod
    def valid_connections(cls):
        return ["impala", "postgres"]

    def collection_query(self, type):
        return {
            'postgres': """
                select count(*) from (
                    select lead(cast("%(col)s" as timestamp), 1) over (order by cast("%(col)s" as timestamp)) - cast("%(col)s" as timestamp) as diff, "%(col)s" from "%(schema)s"."%(table)s"
                ) t where diff > interval '1 day'
            """ % self.query_settings,
            'impala': """
                select count(*) from (
                    select abs(datediff(lead(cast(`%(col)s` as timestamp), 1) over (order by cast(`%(col)s` as timestamp)), 
                    cast(`%(col)s` as timestamp))) as diff, `%(col)s` from `%(schema)s`.`%(table)s`
                ) t where diff > 1
            """ % self.query_settings
        }[type]


    def failed_rows_query(self, type):
        return {
            'postgres': """
                select gap_start, gap_end from (
                    select "%(col)s" as gap_start, cast("%(col)s" as timestamp) + diff as gap_end from 
                        (
                            select lead(cast("%(col)s" as timestamp), 1) over (order by cast("%(col)s" as timestamp)) - cast("%(col)s" as timestamp) as diff, "%(col)s" from "%(schema)s"."%(table)s") t where diff > interval '1 day' limit 10000
                        ) t2
                    where gap_end is not null
            """ % self.query_settings,
            'impala': """
                select gap_start, gap_end from (
                    select `%(col)s` as gap_start, cast(`%(col)s` as timestamp) + interval diff days as gap_end from 
                        (
                            select abs(datediff(lead(cast(`%(col)s` as timestamp), 1) over (order by cast(`%(col)s` as timestamp)), cast(`%(col)s` as timestamp))) as diff, `%(col)s` from `%(schema)s`.`%(table)s`) t where diff > 1 limit 10000
                        ) t2
                    where gap_end is not null
            """ % self.query_settings
        }[type]

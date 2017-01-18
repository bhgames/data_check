
from checks.base_check import BaseCheck

class IdGapCheck(BaseCheck):

    @classmethod
    def valid_connections(cls):
        return ["impala", "postgres"]

    def collection_query(self, type):
        return {
            'postgres': """
                select count(*) from (select abs((lead(cast("%(col)s" as int), 1) over (order by cast("%(col)s" as int)) - cast("%(col)s" as int))) as diff, 
                                            "%(col)s" from "%(schema)s"."%(table)s"
                ) t where diff > %(threshold)s
            """ % self.query_settings,
            'impala': """
                select count(*) from (select abs((lead(cast(`%(col)s` as int), 1) over (order by cast(`%(col)s` as int)) - cast(`%(col)s` as int))) as diff, 
                                            `%(col)s` from `%(schema)s`.`%(table)s`
                ) t where diff > %(threshold)s
            """ % self.query_settings
        }[type]


    def failed_rows_query(self, type):
        return {
            'postgres': """
                select gap_start, gap_end from (
                    select "%(col)s" as gap_start, cast("%(col)s" as int) + diff as gap_end from 
                        (
                            select abs((lead(cast("%(col)s" as int), 1) over (order by cast("%(col)s" as int)) - cast("%(col)s" as int))) as diff, "%(col)s" from "%(schema)s"."%(table)s") t where diff > %(threshold)s limit 1000
                        ) t2
                    where gap_end is not null
            """ % self.query_settings,
            'impala': """
                select gap_start, gap_end from (
                    select `%(col)s` as gap_start, cast(`%(col)s` as int) + diff as gap_end from 
                        (
                            select abs((lead(cast(`%(col)s` as int), 1) over (order by cast(`%(col)s` as int)) - cast(`%(col)s` as int))) as diff, `%(col)s` from `%(schema)s`.`%(table)s`) t where diff > %(threshold)s limit 1000
                        ) t2
                    where gap_end is not null
            """ % self.query_settings
        }[type]


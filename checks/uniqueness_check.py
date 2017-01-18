
from checks.base_check import BaseCheck
from connections.impala_connection import ImpalaConnection


class UniquenessCheck(BaseCheck):

    @classmethod
    def valid_connections(cls):
        return ["impala", "postgres"]


    def collection_query(self, type):
        return {
            'postgres': 'select count("%(col)s") as count, count(distinct "%(col)s") as dist_count from "%(schema)s"."%(table)s"' % self.query_settings,
            'impala': 'select count(`%(col)s`) as count, count(distinct `%(col)s`) as dist_count from `%(schema)s`.`%(table)s`' % self.query_settings
        }[type]


    def failed_rows_query(self, type):
        return {
            'postgres': ' select "%(col)s" from (select "%(col)s", count(*) as count from "%(schema)s"."%(table)s" group by "%(col)s") t where count > 1 limit 10000' % self.query_settings,
            'impala': ' select `%(col)s` from (select `%(col)s`, count(*) as count from `%(schema)s`.`%(table)s` group by `%(col)s`) t where count > 1 limit 10000' % self.query_settings
        }[type]


    def inner_run(self, db):
        cur = db.cursor()

        query = self.collection_query(self.config['data_source_type'])
        self.add_log("collection", "Run query %s" % (query))

        cur.execute(query)

        row = cur.fetchone()

        self.add_log("result", "Query came back with count %s and distinct count of %s" %(row[0], row[1]))

        self.failed = row[0] != row[1]
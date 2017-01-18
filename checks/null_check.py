
from checks.base_check import BaseCheck


class NullCheck(BaseCheck):

    @classmethod
    def valid_connections(cls):
        return ["impala", "postgres"]


    def collection_query(self, type):
        return {
            'postgres': 'select count(*) from "%(schema)s"."%(table)s" where "%(col)s" is null' % self.query_settings,
            'impala': 'select count(*) from `%(schema)s`.`%(table)s` where `%(col)s` is null' % self.query_settings
        }[type]


    def failed_rows_query(self, type):
        return {
            'postgres': 'select * from "%(schema)s"."%(table)s" where "%(col)s" is null limit 10000' % self.query_settings,
            'impala': 'select * from `%(schema)s`.`%(table)s` where `%(col)s` is null limit 10000' % self.query_settings
        }[type]
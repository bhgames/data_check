
from checks.base_check import BaseCheck

class ColumnComparisonCheck(BaseCheck):
    @classmethod
    def valid_connections(cls):
        return ["impala", "postgres"]

    def collection_query(self, type):
        return {
            'postgres': ' select count(*) from (select %(expression)s as condition from "%(schema)s"."%(table)s") t where t.condition = false' % self.query_settings,
            'impala': ' select count(*) from (select %(expression)s as condition from `%(schema)s`.`%(table)s`) t where t.condition = false' % self.query_settings
        }[type]


    def failed_rows_query(self, type):
        return {
            'postgres': 'select * from (select *, %(expression)s as condition from "%(schema)s"."%(table)s") t where t.condition = false limit 10000' % self.query_settings,
            'impala': 'select * from (select *, %(expression)s as condition from `%(schema)s`.`%(table)s`) t where t.condition = false limit 10000' % self.query_settings
        }[type]
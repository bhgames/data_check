"""
    Schemas used by the Flask server to present SQLAlchemy models in the models folder.
"""

from marshmallow import Schema, fields, pprint, pre_load

class CheckMetadataSchema(Schema):
    column = fields.Str()
    expression = fields.Str()
    threshold = fields.Integer()


class CheckSchema(Schema):
    id = fields.Integer()
    check_type = fields.Str()
    check_metadata = fields.Nested(CheckMetadataSchema())

    @classmethod
    def default_json(cls):
        """
            Used by the NEW action in Flask, to generate a dummy object that can
            be sent down with id=new for the form on the React-side to use.

            This makes it easy to work with new or existing objects in the form,
            it only needs to look at ID to know to POST or PUT, but functionality
            is otherwise identical.
        """
        return {
            "id": 'new',
            "check_metadata": {
                "column": ''
            },
            "check_type": 'CheckType.uniqueness'
        }


class RuleConditionalSchema(Schema):
    column = fields.Str()
    count = fields.Str()
    pattern = fields.Str()


class RuleSchema(Schema):
    id = fields.Integer()
    condition = fields.Str()
    conditional = fields.Nested(RuleConditionalSchema())
    checks = fields.Nested(CheckSchema(), many=True)
    children = fields.Nested('self', many=True)

    class Meta:
        additional = ()

    @classmethod
    def default_json(cls):
        """
            Used by the NEW action in Flask, to generate a dummy object that can
            be sent down with id=new for the form on the React-side to use.

            This makes it easy to work with new or existing objects in the form,
            it only needs to look at ID to know to POST or PUT, but functionality
            is otherwise identical.
        """
        return {
            "id": 'new',
            "conditional": {
                "column": ''
            },
            "condition": 'RuleCondition.if_col_present',
            "checks": [],
            "children": []
        }


class DataSourceSchema(Schema):
    id = fields.Integer()
    host = fields.Str()
    port = fields.Number()
    user = fields.Str()
    password = fields.Str()
    schemas = fields.List(fields.String)
    data_source_type = fields.Str()

    class Meta:
        additional = ()

    @classmethod
    def default_json(cls):
        """
            Used by the NEW action in Flask, to generate a dummy object that can
            be sent down with id=new for the form on the React-side to use.

            This makes it easy to work with new or existing objects in the form,
            it only needs to look at ID to know to POST or PUT, but functionality
            is otherwise identical.
        """
        return {
            "id": 'new',
            "host": '',
            "port": 21050,
            "user": '',
            "password": '',
            "schemas": [],
            "data_source_type": "DataSourceType.impala"
        }


class JobTemplateSchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    parallelization = fields.Number()
    rules = fields.Nested(RuleSchema(), many=True)
    checks = fields.Nested(CheckSchema(), many=True)
    data_sources = fields.Nested(DataSourceSchema(), many=True)

    class Meta:
        additional = ()

    @classmethod
    def default_json(cls):
        """
            Used by the NEW action in Flask, to generate a dummy object that can
            be sent down with id=new for the form on the React-side to use.

            This makes it easy to work with new or existing objects in the form,
            it only needs to look at ID to know to POST or PUT, but functionality
            is otherwise identical.
        """
        return {
            "id": 'new',
            "name": '',
            "parallelization": 1,
            "rules": [],
            "data_sources": [],
            "checks": []
        }



class LogSchema(Schema):
    id = fields.Integer()
    log = fields.List(fields.Dict)
    loggable_type = fields.Str()
    loggable_id = fields.Integer()
 

class JobRunSchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    scheduled_at = fields.DateTime()
    rejected_at = fields.DateTime()
    failed_at = fields.DateTime()
    cancelled_at = fields.DateTime()
    run_at = fields.DateTime()
    finished_at = fields.DateTime()
    parallelization = fields.Number()
    status = fields.Str()
    job_template = fields.Nested(JobTemplateSchema())
    job_template_name = fields.Method("set_template_name", dump_only=True)
    all_connected_logs = fields.Nested(LogSchema(), many=True)

    HIDDEN_FROM_LIST=["all_connected_logs"]

    def set_template_name(self, jr):
        return jr.job_template.name


class ScheduleSchema(Schema):
    id = fields.Integer()
    schedule_config = fields.Dict()
    job_templates = fields.Nested(JobTemplateSchema, only=["id", "name", "parallelization"], many=True)
    job_templates_names = fields.Method("set_template_names", dump_only=True)
    active = fields.Bool()

    def set_template_names(self, sch):
        return ",".join(map(lambda jt: jt.name, sch.job_templates))


    @classmethod
    def default_json(cls):
        """
            Used by the NEW action in Flask, to generate a dummy object that can
            be sent down with id=new for the form on the React-side to use.

            This makes it easy to work with new or existing objects in the form,
            it only needs to look at ID to know to POST or PUT, but functionality
            is otherwise identical.
        """
        return {
            "id": 'new',
            "schedule_config": {
                "hour": 0,
                "minute": 0,
                "day_of_week": ''
            },
            "active": True,
            "job_templates": [],
            "job_templates_names": ""
        }


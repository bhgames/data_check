"""
    Schemas used by the Flask server to present SQLAlchemy models in the models folder.
"""

from marshmallow import Schema, fields, pprint

class CheckMetadataSchema(Schema):
    column = fields.Str()


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
    schemas =  fields.List(fields.String)
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
            "data_sources": []
        }



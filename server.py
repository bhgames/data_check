from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from inflection import camelize, singularize

import models.helpers.base
import traceback
from sqlalchemy import create_engine, MetaData, desc
engine = create_engine('postgresql://localhost:5432/data_check')
models.helpers.base.init(engine) # Initialize base declarative class.

from models.check import Check, CheckType
from models.rule import Rule, RuleCondition
from models.job_template import JobTemplate
from models.helpers.schemas import JobTemplateSchema, CheckSchema, RuleSchema, DataSourceSchema, JobRunSchema
from models.schedule import Schedule
from models.job_run import JobRun
from models.data_source import DataSource, DataSourceType

import datetime
now = datetime.datetime.now

app = Flask(__name__)
CORS(app)
db_session = models.helpers.base.db_session

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def get_class_from_type(type):
    return eval(singularize(camelize(type)))


def get_class_schema_from_type(type):
    return eval(singularize(camelize(type)) + "Schema")


def enum_from_value(val):
    klazz = eval(val.split(".")[0])
    value = getattr(klazz, val.split(".")[1])
    return value


def update_attribute(obj, key, value):
    """
        TODO Figure out a way to detect if a key is an ENUM, instead of using a Global on the object's Class.
    """

    if key == "id":
        return False

    if(hasattr(obj, key) == False):
        return False # Ignore attributes that aren't real attributes.

    if(hasattr(obj, "ENUMS") == False):
        raise ValueError("ENUMS is not defined for this model!")

    if(key in obj.ENUMS):
        setattr(obj, key, enum_from_value(value))
    elif(hasattr(getattr(obj.__class__, key).property, 'mapper')):
        #Means this is an association of some kind.
        klazz = getattr(obj.__class__, key).property.mapper.class_

        if(isinstance(value, list)):            
            mapped = [existing_or_new_instance_from_dict(klazz, v) for v in value]
        else:
            mapped = existing_or_new_instance_from_dict(klazz, value)

        setattr(obj, key, mapped)
    else:
        setattr(obj, key, value)


def existing_or_new_instance_from_dict(klazz, v):
    """
        Given a dict of values representing an instance of an association,
        we need to either reify this from the DB or create one anew.
    """
    if(v["id"]):
        return db_session.query(klazz).get(v["id"])
    else:
        return klazz(**v)


def update_attributes(obj, json):
    [update_attribute(obj, key, json[key]) for key in json.keys()]


@app.route('/<type>', methods=['POST'])
def new_item_save(type):
    klazz = get_class_from_type(type)
    new_inst = klazz()
    update_attributes(new_inst, request.json)
    db_session.add(new_inst)
    db_session.commit()
    id = new_inst.id
    return jsonify({ "id": id })


@app.route('/job_runs', methods=['POST'])
def new_job_run_save():
    """
        JobRuns cannot be created classically from the GUI, only by hitting the Run button on a template,
        which creates and schedules the job run to be run immediately. Normally job runs are created
        by the background scheduler.
    """
    jt = db_session.query(JobTemplate).get(request.json["job_template_id"])
    jr = JobRun.create_job_run(jt, now())
    return jsonify({ "id": jr.id })


@app.route('/<type>', methods=['GET'])
def get_items(type):
    klazz = get_class_from_type(type)
    sch_klazz = get_class_schema_from_type(type)
    qr = db_session.query(klazz).order_by(desc(klazz.__table__.c.updated_at))
    qr = qr.all()
    sch = sch_klazz(many=True)

    if(hasattr(sch_klazz, "HIDDEN_FROM_LIST")):
        sch = sch_klazz(many=True, exclude=sch_klazz.HIDDEN_FROM_LIST)
    else:
        sch = sch_klazz(many=True)

    return sch.dumps(qr)


@app.route('/<type>/new', methods=['GET'])
def new_item(type):
    sch_klazz = get_class_schema_from_type(type)
    return jsonify(sch_klazz.default_json())


@app.route('/<type>/<id>', methods=['GET'])
def get_item(type, id):
    klazz = get_class_from_type(type)
    sch_klazz = get_class_schema_from_type(type)
    qr = db_session.query(klazz).get(id)
    sch = sch_klazz()
    return sch.dumps(qr)


@app.route('/<type>/<id>', methods=['PUT'])
def update_item(type, id):
    klazz = get_class_from_type(type)
    qr = db_session.query(klazz).get(id)
    print request.json
    update_attributes(qr, request.json)
    db_session.add(qr)
    db_session.commit()
    return jsonify({})


@app.route('/<type>/<id>', methods=['DELETE'])
def delete_item(type, id):
    klazz = get_class_from_type(type)
    qr = db_session.query(klazz).get(id)
    db_session.delete(qr)
    db_session.commit()
    return jsonify({})


if __name__ == "__main__":
    app.run()
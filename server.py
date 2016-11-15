from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from inflection import camelize, singularize

import models.helpers.base
import traceback
from sqlalchemy import create_engine
from sqlalchemy import MetaData
engine = create_engine('postgresql://localhost:5432/data_check')
models.helpers.base.init(engine) # Initialize base declarative class.

from models.check import Check, CheckSchema, CheckType
from models.rule import Rule, RuleSchema, RuleCondition
from models.job_template import JobTemplate
from models.schedule import Schedule

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

    if(hasattr(obj, "ENUMS") == False):
        raise ValueError("ENUMS is not defined for this model!")

    if(key in obj.ENUMS):
        setattr(obj, key, enum_from_value(value))
    else:
        setattr(obj, key, value)


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


@app.route('/<type>', methods=['GET'])
def get_items(type):
    klazz = get_class_from_type(type)
    sch_klazz = get_class_schema_from_type(type)
    qr = db_session.query(klazz)
    qr = qr.all()
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
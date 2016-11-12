from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

import models.helpers.base
import traceback
from sqlalchemy import create_engine
from sqlalchemy import MetaData
engine = create_engine('postgresql://localhost:5432/data_check')
models.helpers.base.init(engine) # Initialize base declarative class.

from models.check import Check, CheckSchema, CheckType
from models.rule import Rule
from models.job_template import JobTemplate
from models.schedule import Schedule

app = Flask(__name__)
CORS(app)
db_session = models.helpers.base.db_session


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

def get_check_type_from_params():
    check_type_class = eval(request.json['check_type'].split(".")[0])
    check_type_value = getattr(check_type_class, request.json['check_type'].split(".")[1])
    return check_type_value

@app.route('/checks', methods=['POST'])
def new_check_save():
    c = Check(check_type=get_check_type_from_params(), check_metadata=request.json['check_metadata'])
    db_session.add(c)
    db_session.commit()
    id = c.id
    return jsonify({ "id": id })


@app.route('/checks', methods=['GET'])
def get_checks():
    qr = db_session.query(Check).add_columns("id", "check_type", "check_metadata")
    qr = qr.all()
    sch = CheckSchema(many=True)
    return sch.dumps(qr)


@app.route('/checks/new', methods=['GET'])
def new_check():
    return jsonify(
        {
            "id": 'new',
            "check_metadata": {
                "column": ''
            },
            "check_type": 'CheckType.uniqueness'
        }
    )


@app.route('/checks/<id>', methods=['GET'])
def get_check(id):
    qr = db_session.query(Check).get(id)
    sch = CheckSchema()
    return sch.dumps(qr)


@app.route('/checks/<id>', methods=['PUT'])
def update_check(id):
    qr = db_session.query(Check).get(id)
    qr.check_type = get_check_type_from_params()
    qr.check_metadata = request.json['check_metadata']
    db_session.add(qr)
    db_session.commit()
    return jsonify({})



@app.route('/checks/<id>', methods=['DELETE'])
def delete_check(id):
    qr = db_session.query(Check).get(id)
    db_session.delete(qr)
    db_session.commit()
    return jsonify({})

if __name__ == "__main__":
    app.run()
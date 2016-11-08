from flask import Flask, request, jsonify

import models.helpers.base
import traceback
from sqlalchemy import create_engine
from sqlalchemy import MetaData
engine = create_engine('postgresql://localhost:5432/data_check')
models.helpers.base.init(engine) # Initialize base declarative class.

from models.check import Check
from models.rule import Rule
from models.job_template import JobTemplate
from models.schedule import Schedule

app = Flask(__name__)
Session = models.helpers.base.Session

@app.route('/checks', methods=['POST'])
def new_check():
    s = Session()
    c = Check(check_type=request.json['check_type'], check_metadata=request.json['check_metadata'])
    s.add(c)
    s.commit()
    id = c.id
    s.close()
    return jsonify({ "id": id })

if __name__ == "__main__":
    app.run()
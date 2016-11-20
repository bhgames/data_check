from celery import Celery
import models.helpers.base

if(hasattr(models.helpers.base, "db_session") == False):
    print "Run"
    from sqlalchemy import create_engine, MetaData
    engine = create_engine('postgresql://localhost:5432/data_check')
    models.helpers.base.init(engine)

import models.job_run
import models.data_source
import models.check
import models.schedule
import models.rule
import models.job_template
import models.log

db_session = models.helpers.base.db_session

app = Celery('job_runs', broker='amqp://guest@localhost//')

@app.task
def run_job(job_run_id):
    jr = db_session.query(models.job_run.JobRun).get(job_run_id)
    jr.run()


@app.task
def run_check(source_id, table_name_string, check_id, job_run_id):
    check = db_session.query(models.check.Check).get(check_id)
    job_run = db_session.query(models.job_run.JobRun).get(job_run_id)
    source = db_session.query(models.data_source.DataSource).get(source_id)
    check.run(job_run, source, table_name_string)


@app.task
def register_finished(some_other_arg, job_run_id):
    """
        Admittedly Im not sure what first arg is, but it has to be there to get to the one I want. TODO figure out what it is.
    """
    jr = db_session.query(models.job_run.JobRun).get(job_run_id)

    if jr.status == models.job_run.JobRunStatus.running:
        jr.set_finished()
        db_session.add(jr)
        db_session.commit()



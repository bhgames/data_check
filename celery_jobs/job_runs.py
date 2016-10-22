from celery import Celery
import models.helpers.base
from models.data_source import DataSource

Session = models.helpers.base.Session
app = Celery('job_runs', broker='amqp://guest@localhost//')

@app.task
def run_job(id):
    session = Session()
    jr = session.query(JobRun).get(job_run_id)
    jr.run()
    session.close()


@app.task
def run_check(job_run_id, source_id, table_name_string, check_id):
    session = Session()
    check = session.query(Check).get(check_id)
    job_run = session.query(JobRun).get(job_run_id)
    source = session.query(DataSource).get(source_id)
    check.run(job_run, source, table_name_string)
    session.close()


@app.task
def register_finished(job_run_id):
    session = Session()
    jr = session.query(JobRun).get(job_run_id)

    if jr.status == JobRunStatus.running:
        jr.set_finished()
        session.add(jr)
        session.commit()
        session.close()

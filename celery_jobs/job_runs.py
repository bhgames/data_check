from celery import Celery
import models.helpers.base
import models

Session = models.helpers.base.Session
app = Celery('job_runs', broker='amqp://guest@localhost//')

@app.task
def run_job(job_run_id):
    session = Session()
    jr = session.query(models.job_run.JobRun).get(job_run_id)
    jr.run()
    session.close()


@app.task
def run_check(source_id, table_name_string, check_id, job_run_id):
    session = Session()
    check = session.query(models.check.Check).get(check_id)
    job_run = session.query(models.job_run.JobRun).get(job_run_id)
    source = session.query(models.data_source.DataSource).get(source_id)
    check.run(job_run, source, table_name_string)
    session.close()


@app.task
def register_finished(job_run_id):
    session = Session()
    jr = session.query(models.job_run.JobRun).get(job_run_id)

    if jr.status == models.job_run.JobRunStatus.running:
        jr.set_finished()
        session.add(jr)
        session.commit()
        session.close()

from celery import Celery
import models.helpers.base
import models

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
def register_finished(job_run_id):
    jr = db_session.query(models.job_run.JobRun).get(job_run_id)

    if jr.status == models.job_run.JobRunStatus.running:
        jr.set_finished()
        db_session.add(jr)
        db_session.commit()

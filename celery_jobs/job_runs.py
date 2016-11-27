from celery import Celery
from celery.schedules import crontab

import models.helpers.base

if(hasattr(models.helpers.base, "db_session") == False):
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
import datetime
from subprocess import call
from time import sleep
from os.path import isfile
now = datetime.datetime.now

CELERY_TIMEZONE = 'America/Chicago'

db_session = models.helpers.base.db_session

app = Celery('job_runs', broker='amqp://guest@localhost//')
app.config_from_object('celery_jobs.celeryconfig')

from celery.signals import worker_shutdown


def kill_beat():
    if isfile("celerybeat.pid"):
        call(["kill $(cat celerybeat.pid)"], shell=True)
    

@worker_shutdown.connect
def worker_shutdown(**kwargs):
    """
        When you ctrl-c bin/celery, it should also kill the beat process.
    """
    kill_beat()


@app.task
def reset_beat():
    """
        Beat schedule can only be updated by restarting it...so to avoid having to bring in Django for true dynamic
        scheduling with all that paperwork, I just find the PID and nuke the beat. Then restart it.
        Part of the beat's cron is always to nuke itself every five minutes. Clever, eh?

        TODO replace this with something more formalized if this ever leaves beta.
    """

    kill_beat()
    sleep(1)
    call(["nohup celery -A celery_jobs.job_runs beat --loglevel=info --logfile beat.out &"], shell=True)


@app.task
def create_jobs_for_schedule(schedule_id):
    schedule = db_session.query(models.schedule.Schedule).get(schedule_id)
    [models.job_run.JobRun.create_job_run(jt) for jt in schedule.job_templates]


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




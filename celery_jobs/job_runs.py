from celery import Celery, Task
from celery.schedules import crontab
import yaml
import models.helpers.base

if(hasattr(models.helpers.base, "db_session") == False):
    from sqlalchemy import create_engine, MetaData
    engine = models.helpers.base.get_new_engine()
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
from os import environ
now = datetime.datetime.now

CELERY_TIMEZONE = 'America/Chicago'

with open('config/config.yml', 'r') as f:
    config = yaml.load(f)

conf = config['message_passing'][environ['DCHK_ENV']]
broker = (conf['type'] + '://' + (conf['username'] if 'username' in conf else '') + 
         (':' + conf['password'] if 'password' in conf else '') + '@' + 
         conf['host'] + (':' + str(conf['port']) if 'port' in conf else '') + '/' + (str(conf['instance']) if 'instance' in conf else ''))
app = Celery('job_runs', broker=broker, backend=broker)
app.config_from_object('celery_jobs.celeryconfig')

from celery.signals import worker_shutdown, celeryd_after_setup

def kill_beat():
    if isfile("celerybeat.pid"):
        call(["kill $(cat celerybeat.pid)"], shell=True)
    

@worker_shutdown.connect
def worker_shutdown(**kwargs):
    """
        When you ctrl-c bin/celery, it should also kill the beat process.
    """
    kill_beat()


@celeryd_after_setup.connect
def setup_engine(**kwargs):
    # Since we have forked, we need a new engine and db_session.
    engine = models.helpers.base.get_new_engine()
    models.helpers.base.init(engine)
    db_session = models.helpers.base.db_session
    models.job_run.db_session = db_session
    models.data_source.db_session = db_session
    models.check.db_session = db_session
    models.schedule.db_session = db_session
    models.rule.db_session = db_session
    models.job_template.db_session = db_session
    models.log.db_session = db_session


def setup_connection():
    # Use a method because .db_Session reassigned after forking, need to make sure
    # you get the most up-to-date value.
    return models.helpers.base.db_session


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
    db_session = setup_connection()
    schedule = db_session.query(models.schedule.Schedule).get(schedule_id)
    [models.job_run.JobRun.create_job_run(jt) for jt in schedule.job_templates]


@app.task
def run_job(job_run_id):
    db_session = setup_connection()
    jr = db_session.query(models.job_run.JobRun).get(job_run_id)
    jr.run()


@app.task
def run_check(source_id, table_name_string, check_id, job_run_id):
    try:
        db_session = setup_connection()
        check = db_session.query(models.check.Check).get(check_id)
        job_run = db_session.query(models.job_run.JobRun).get(job_run_id)
        source = db_session.query(models.data_source.DataSource).get(source_id)
        check.run(job_run, source, table_name_string)
    except Exception as exc:
        if(run_check.request.retries == 3):
            job_run.set_failed()
            db_session.commit()
        else:
            raise run_check.retry(exc=exc, countdown=60*run_check.request.retries)


@app.task
def register_finished(some_other_arg, job_run_id):
    """
        Admittedly Im not sure what first arg is, but it has to be there to get to the one I want. TODO figure out what it is.
    """
    db_session = setup_connection()

    jr = db_session.query(models.job_run.JobRun).get(job_run_id)

    if jr.status == models.job_run.JobRunStatus.running:
        jr.set_finished()
        db_session.add(jr)
        db_session.commit()




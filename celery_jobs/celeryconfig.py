from celery.schedules import crontab
import models.helpers.base

db_session = models.helpers.base.db_session

CELERYBEAT_SCHEDULE = {
    'reset': {
        'task': 'celery_jobs.job_runs.reset_beat',
        'schedule': crontab(minute='*/5'),
        'args': tuple()
    }
}

schedules = db_session.query(models.schedule.Schedule).filter(models.schedule.Schedule.active == True).all()

for s in schedules:
    cleaned_schedule = {}
    for key in s.schedule_config.keys():
        if s.schedule_config[key] != '':
            cleaned_schedule[key] = s.schedule_config[key]

    CELERYBEAT_SCHEDULE['schedule-' + str(s.id)] = {
        'task': 'celery_jobs.job_runs.create_jobs_for_schedule',
        'schedule': crontab(**cleaned_schedule),
        'args': tuple(s.id)
    }

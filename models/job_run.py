
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Enum, Table, DateTime
from sqlalchemy.orm import relationship, backref
import models.helpers.base
from sqlalchemy.dialects.postgresql import JSONB
from models.helpers.timestamps_triggers import timestamps_triggers
Base = models.helpers.base.Base
Session = models.helpers.base.Session
from datetime.datetime import now
from celery_jobs.job_runs import run_job
from celery_jobs.job_runs import run_check
from celery_jobs.job_runs import register_finished
from celery import chord
from models.log import Log, HasLogs
import sys
import enum
import numpy as np

class JobRunStatus(enum.Enum):
    scheduled = "scheduled"
    running = "running"
    failed = "failed"
    finished = "finished"
    rejected = "rejected"
    cancelled = "cancelled"


class JobRun(Base, HasLogs):
    __tablename__ = 'job_run'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    rejected_at = Column(DateTime)
    failed_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    run_at = Column(DateTime)
    finished_at = Column(DateTime)
    status = Column(Enum(JobRunStatus), nullable=False)
    job_template_id = Column(Integer, ForeignKey('job_template.id'))
    job_template = relationship('JobTemplate')
    job_run_check_logs = relationship('JobRunCheckLog', back_populates="job_run")

    @classmethod
    def create_job_run(cls, job_template, scheduled_run_time):
        session = Session()
        jr = JobRun(
            scheduled_at = scheduled_run_time, 
            status=JobRunStatus.scheduled, 
            job_template=job_template
        )
        session.add(jr)
        session.commit()
        run_job.apply_async(jr.id, eta=scheduled_run_time)


    def set_failed(self):
        print str(sys.exc_info())
        self.status = JobRunStatus.failed
        self.failed_at = now()
        self.logs[0].new_error_event()


    def set_finished(self):
        self.status = JobRunStatus.finished
        self.finished_at = now()
        self.logs[0].add_log("finished", "Job Finished at %s" % (self.finished_at))


    def run(self):
        session = Session()
        session.add(self)

        try:
            self.status = JobRunStatus.running
            self.run_at = now()
            log = Log(job_run=self)
            log.add_log("started", "Job Started at %s" % (self.run_at))
            self.logs.append(log)
            session.add(log)

            checks_to_run = []

            # Let the rules populate the checks they wish to run.
            # Don't forget to first open connections on all sources so they can be queried.
            [source.open_connection() for source in self.job_template.data_sources]
            map(lambda r: r.run(self, checks_to_run, session), self.job_template.rules)
            [source.close_connection() for source in self.job_template.data_sources]

            # Dedupe checks_to_run even against checks. Expect of tuples of format (DataSource, table_name_string, Check)
            seen = set()
            seen_add = seen.add
            checks_to_run = [c for c in checks_to_run if not ([c[0].id, c[1], c[2].id] in seen or seen_add([c[0].id, c[1], c[2].id]))]

            # Bucketize checks based on parallelization chosen. Each bucket runs sequentially.
            checks_by_parallelization = np.split(checks_to_run, self.parallelization)

            # Run each bucket of checks in a separate celery worker.
            chord([run_check.s(map(lambda c: [c[0].id, c[1], c[2].id], chks)) for chks in checks_by_parallelization])(register_finished.s(self.id))
        except Exception:
            self.set_failed()
        
        session.commit()


timestamps_triggers(JobRun)

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Enum, Table, DateTime
from sqlalchemy.orm import relationship, backref
import models.helpers.base
from sqlalchemy.dialects.postgresql import JSONB
from models.helpers.timestamps_triggers import timestamps_triggers
Base = models.helpers.base.Base
db_session = models.helpers.base.db_session
import datetime
now = datetime.datetime.now
import celery_jobs.job_runs
from celery import chord, chain, group
from models.log import Log, HasLogs
import sys
import enum
import numpy as np
import traceback

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
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    scheduled_at = Column(DateTime, nullable=False)
    rejected_at = Column(DateTime)
    failed_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    run_at = Column(DateTime)
    finished_at = Column(DateTime)
    status = Column(Enum(JobRunStatus), nullable=False)
    job_template_id = Column(Integer, ForeignKey('job_template.id'))
    job_template = relationship('JobTemplate')
    # .logs returns only logs where loggable_type = JobRun and loggable_id = this id
    # all_connected_logs grabs logs for any connected object where the job_run_id on logs is set.
    # So you can use this to see everything that happened for a job.
    all_connected_logs = relationship('Log')

    ENUMS=["status"]

    @classmethod
    def create_job_run(cls, job_template):
        jr = JobRun(
            scheduled_at = now(), 
            status=JobRunStatus.scheduled, 
            job_template=job_template
        )
        db_session.add(jr)
        db_session.commit()
        # Need to use 3s buffer to give time for postgres commit to propagate to the "real"
        # postgres. Instant async run causes race condition where it runs before save completed.
        celery_jobs.job_runs.run_job.apply_async([jr.id], countdown=3)
        return jr


    def set_failed(self):
        traceback.print_exc()
        self.status = JobRunStatus.failed
        self.failed_at = now()
        self.get_log(job_run=self).new_error_event()


    def set_finished(self):
        self.status = JobRunStatus.finished
        self.finished_at = now()
        self.get_log(job_run=self).add_log("finished", "Job Finished at %s" % (self.finished_at))


    def run(self):
        db_session.add(self)
        log = self.get_log(job_run=self)

        try:
            self.status = JobRunStatus.running
            self.run_at = now()
            print self.run_at
            
            log.add_log("started", "Job Started at %s" % (self.run_at))

            checks_to_run = []

            # Let the rules populate the checks they wish to run.
            # Don't forget to first open connections on all sources so they can be queried.
            [source.open_connection() for source in self.job_template.data_sources]
            map(lambda r: r.run(self, checks_to_run), self.job_template.rules)
            [source.close_connection() for source in self.job_template.data_sources]

            # Dedupe checks_to_run even against checks. Expect of tuples of format (DataSource, table_name_string, Check)
            seen = set()
            seen_add = seen.add
            checks_to_run = [c for c in checks_to_run if not ((c[0].id, c[1], c[2].id) in seen or seen_add((c[0].id, c[1], c[2].id)))]

            if len(checks_to_run) > 0:
                # Bucketize checks based on parallelization chosen. Each bucket runs sequentially.
                checks_by_parallelization = np.split(np.array(checks_to_run), self.job_template.parallelization)

                # Run each bucket of checks in a separate celery worker, by turning each subarray into an array of celery run check
                # job signatures, and then splatting each array of run check signatures into a chain(requiring them to be done one 
                # at a time in each chain), then you group all chains together so they run in parallel. Each chain is a worker.
                # Then finally you call register finished when all done.
                separate_queues = [map(lambda c: celery_jobs.job_runs.run_check.si(c[0].id, c[1], c[2].id, self.id), chks) for chks in checks_by_parallelization]
                sep_chains = [chain(*queue) for queue in separate_queues]
                group_of_chains = (group(*sep_chains) | celery_jobs.job_runs.register_finished.s(self.id)).apply_async()
            else:
                self.set_finished()

        except Exception:
            self.set_failed()

        db_session.add(log)
        db_session.commit()


timestamps_triggers(JobRun)
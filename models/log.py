from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Enum, Table, DateTime
from sqlalchemy.orm import relationship, backref
import models.helpers.base
from sqlalchemy.dialects.postgresql import JSONB
from models.helpers.timestamps_triggers import timestamps_triggers
Base = models.helpers.base.Base
db_session = models.helpers.base.db_session
import datetime
now = datetime.datetime.now
from celery import chord
import sys
import enum
import numpy as np
from sqlalchemy import event, and_
from sqlalchemy.orm import foreign, remote
from sqlalchemy.orm.attributes import flag_modified    

import traceback

class HasLogs(object):
    """
        HasLogs mixin, creates a relationship to
        the log_association table for each loggable.
    """

    def get_log(self, job_run=None):
        if job_run == None:
            raise ValueError("ERROR: Passing job_run of None will cause disconnected log.")

        if hasattr(self, 'cached_current_log'):
            return self.cached_current_log

        log = db_session.query(Log).filter_by(job_run=job_run, loggable_type=self.__class__.__name__.lower(), loggable_id=self.id).first()

        if not log:
            log = Log(job_run=job_run)
            self.logs.append(log)

        db_session.add(log)

        self.cached_current_log = log

        return log


class Log(Base):
    __tablename__ = "log"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    log = Column(JSONB, nullable=True)
    results_csv = Column(String, nullable=True)
    job_run_id = Column(Integer, ForeignKey('job_run.id'), nullable=False)
    job_run = relationship('JobRun')
    loggable_type = Column(String, nullable=False)
    loggable_id = Column(Integer, nullable=False)
    
    @classmethod
    def new_event(cls, event, message, metadata = {}):
        return { "event": event, "message": message, "metadata": metadata, "time": str(now()) }

    
    def new_error_event(self, failure_msg = None, metadata = {}):

        failure_msg = "Job Failed at %s" % str(now()) if not failure_msg else failure_msg
        tracebackm = { "traceback": traceback.format_exc() }
        tracebackm.update(metadata)
        return self.add_log(
                "failed", 
                failure_msg, 
                tracebackm
            )


    def add_log(self, event, message, metadata = {}):
        if not self.log:
            self.log = []
        self.log.append(self.__class__.new_event(event, message, metadata))

        # http://stackoverflow.com/questions/30088089/sqlalchemy-json-typedecorator-not-saving-correctly-issues-with-session-commit
        flag_modified(self, "log")


@event.listens_for(HasLogs, "mapper_configured", propagate=True)
def setup_listener(mapper, class_):
    name = class_.__name__
    loggable_type = name.lower()
    class_.logs = relationship(Log,
                        primaryjoin=and_(
                                        class_.id == foreign(remote(Log.loggable_id)),
                                        Log.loggable_type == loggable_type
                                    ),
                        backref=backref(
                                "parent_%s" % loggable_type,
                                primaryjoin=remote(class_.id) == foreign(Log.loggable_id)
                                ),
                        cascade="all, delete-orphan")


    @event.listens_for(class_.logs, "append")
    def append_address(target, value, initiator):
        value.loggable_type = loggable_type


timestamps_triggers(Log)

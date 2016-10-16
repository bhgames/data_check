from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Enum, Table, DateTime
from sqlalchemy.orm import relationship, backref
import models.helpers.base
from sqlalchemy.dialects.postgresql import JSONB
from models.helpers.timestamps_triggers import timestamps_triggers
Base = models.helpers.base.Base
Session = models.helpers.base.Session
from datetime.datetime import now
from celery import chord
import sys
import enum
import numpy as np
from sqlalchemy import event

class HasLogs(object):
    """HasLogs mixin, creates a relationship to
    the log_association table for each loggable.

    """


class Log(Base):
    __tablename__ = "log"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    log = Column(JSONB, nullable=True)
    results_csv = Column(String, nullable=True)
    job_run_id = Column(Integer, ForeignKey('job_run.id'))
    job_run = relationship('JobRun')
    loggable_type = Column(String, nullable=False)
    loggable_id = Column(Integer, nullable=False)
    
    @classmethod
    def new_event(cls, event, message, metadata = {}):
        return { "event": event, "message": message, "metadata": metadata }

    
    def new_error_event(self):
        return self.add_log(
                "failed", 
                "Job Failed at %s" % str(now()), 
                { "type":  sys.exc_info()[0], "value":  sys.exc_info()[1], "traceback":  sys.exc_info()[2] }
            )


    def add_log(self, event, message, metadata = {}):
        if not self.log:
            self.log = []
        self.log.append(self.__class__.new_event(event, message, metadata))


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
                                ))

    @event.listens_for(class_.log, "append")
    def append_address(target, value, initiator):
        value.loggable_type = loggable_type


timestamps_triggers(Log)
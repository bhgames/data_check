
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from models.helpers.timestamps_triggers import timestamps_triggers
Base = declarative_base()

import enum
class JobRunStatus(enum.Enum):
    scheduled = "scheduled"
    running = "running"
    failed = "failed"
    finished = "finished"

class JobRun(Base):
    __tablename__ = 'job_runs'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=False)
    status = Column(Enum(JobRunStatus), nullable=False)
    job_template_id = Column(Integer, ForeignKey('job_template.id'))
    job_template = relationship('JobTemplate')
    log = Column(Text, nullable=True)
    job_run_check_logs = relationship('JobRunCheckLog', back_populates="job_run")

class JobRunCheckLog(Base):
    __tablename__ = "job_run_check_logs"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    log = Column(Text, nullable=True)
    results_csv = Column(String, nullable=True)
    job_run_id = Column(Integer, ForeignKey('job_run.id'))
    rule_id = Column(Integer, ForeignKey('rule.id'))
    job_run = relationship('JobRun', back_populates="job_run_check_logs")
    rule = relationship('Rule')

timestamps_triggers(JobRun)
timestamps_triggers(JobRunCheckLog)
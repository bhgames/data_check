
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Enum, Table, DateTime
from sqlalchemy.orm import relationship, backref
import models.helpers.base
from models.helpers.timestamps_triggers import timestamps_triggers
Base = models.helpers.base.Base

import enum
class JobRunStatus(enum.Enum):
    scheduled = "scheduled"
    running = "running"
    failed = "failed"
    finished = "finished"
    rejected = "rejected"
    cancelled = "cancelled"

class JobRun(Base):
    __tablename__ = 'job_run'
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

class JobRunRuleLog(Base):
    """
        One log for each Rule fired.
    """
    __tablename__ = "job_run_rule_log"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    log = Column(Text, nullable=True)
    results_csv = Column(String, nullable=True)
    job_run_id = Column(Integer, ForeignKey('job_run.id'))
    rule_id = Column(Integer, ForeignKey('rule.id'))
    job_run = relationship('JobRun', back_populates="job_run_check_logs")
    rule = relationship('Rule')
    job_run_rule_check_logs = relationship('JobRunRuleCheckLog', back_populates="job_run_rule_log")


class JobRunRuleCheckLog(Base):
    """
        There should be one log for each check on each rule. These can all be concatenated together.
    """
    __tablename__ = "job_run_rule_check_log"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    log = Column(Text, nullable=True)
    results_csv = Column(String, nullable=True)
    job_run_id = Column(Integer, ForeignKey('job_run.id'))
    check_id = Column(Integer, ForeignKey('check.id'))
    rule_id = Column(Integer, ForeignKey('rule.id'))
    job_run_rule_log_id = Column(Integer, ForeignKey('job_run_rule_log.id'))
    job_run_rule_log = relationship('JobRunRuleLog', back_populates="job_run_rule_check_logs")
    check = relationship('Check')
    rule = relationship('Rule')

timestamps_triggers(JobRun)
timestamps_triggers(JobRunRuleLog)
timestamps_triggers(JobRunRuleCheckLog)
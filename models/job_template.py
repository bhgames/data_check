
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Table, DateTime, Enum
from sqlalchemy.orm import relationship, backref
import models.helpers.base
from models.helpers.timestamps_triggers import timestamps_triggers

Base = models.helpers.base.Base

job_templates_rules = Table('job_templates_rules', Base.metadata,
    Column('rule_id', Integer, ForeignKey('rule.id')),
    Column('job_template_id', Integer, ForeignKey('job_template.id')))

job_templates_schedules = Table('job_templates_schedules', Base.metadata,
    Column('schedule_id', Integer, ForeignKey('schedule.id')),
    Column('job_template_id', Integer, ForeignKey('job_template.id')))

data_sources_job_templates = Table('data_sources_job_templates', Base.metadata,
    Column('data_source_id', Integer, ForeignKey('data_source.id')),
    Column('job_template_id', Integer, ForeignKey('job_template.id')))

import enum
class LogLevel(enum.Enum):
    complete = "complete"
    primary_key_only = "primary_key_only"
    status_only = "status_only"

class JobTemplate(Base):
    __tablename__ = 'job_template'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    log_level = Column(Enum(LogLevel), nullable=False)
    name = Column(String, nullable=False)
    parallelization = Column(Integer, default=1, nullable=False)
    job_runs = relationship('JobRun', back_populates="job_template")
    data_sources = relationship('DataSource', back_populates="job_templates", secondary=data_sources_job_templates)
    rules = relationship('Rule', back_populates="job_templates", secondary=job_templates_rules)
    schedules = relationship('Schedule', back_populates='job_templates', secondary=job_templates_schedules)

timestamps_triggers(JobTemplate)
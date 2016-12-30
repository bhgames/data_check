
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Table, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.session import make_transient
import models.helpers.base
from models.helpers.timestamps_triggers import timestamps_triggers
import numpy as np

Base = models.helpers.base.Base
db_session = models.helpers.base.db_session

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
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    log_level = Column(Enum(LogLevel), nullable=False, default=LogLevel.status_only)
    name = Column(String, nullable=False)
    parallelization = Column(Integer, default=1, nullable=False)

    # RO copy is created whenever a JobRun creates, used for holding meta info about it's template even if template changes.
    # We dont make parent id FK because parent template may get deleted at some point. This is for logging.
    read_only = Column(Boolean, default=False, nullable=False)
    parent_job_template_id = Column(Integer, nullable=True)

    job_runs = relationship('JobRun', back_populates="job_template")
    data_sources = relationship('DataSource', secondary=data_sources_job_templates)
    rules = relationship('Rule', back_populates="job_templates", secondary=job_templates_rules)
    schedules = relationship('Schedule', back_populates='job_templates', secondary=job_templates_schedules)
    ENUMS = ["log_level"]


    def become_read_only_clone(self):
        """
            Next time this object is saved it will be saved as a new entry,
            with read_only set to true, parent id set to the cloner row,
            and all it's checks and rules cloned as well.
        """
        
        self.parent_job_template_id = self.id
        self.read_only = True
        rules = self.rules
        ds = self.data_sources # Grab before expunging.
        db_session.expunge(self)
        make_transient(self)

        [r.become_read_only_clone() for r in rules]
        [d.become_read_only_clone() for d in ds]

        self.id = None

        db_session.add(self)
        db_session.commit()

        self.rules = rules
        self.data_sources = ds

    def checks(self):
        seen = set()
        seen_add = seen.add
        all_checks = np.array(map(lambda r: r.checks, self.rules)).flatten()
        checks = [c for c in all_checks if not c.id in seen or seen_add(c.id)]
        return checks

timestamps_triggers(JobTemplate)

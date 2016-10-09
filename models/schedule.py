
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from models.helpers.timestamps_triggers import timestamps_triggers

Base = declarative_base()

job_templates_schedules = Table('job_templates_schedules', Base.metadata,
    Column('schedule_id', Integer, ForeignKey('schedule.id')),
    Column('job_template_id', Integer, ForeignKey('job_template.id')))

class Schedule(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    schedule_config = Column(JSONB, nullable=False)
    job_templates = relationship('JobTemplate', back_populates='schedules', secondary=job_templates_schedules)
    active = Column(Boolean, default=True, nullable=False)

timestamps_triggers(Schedule)

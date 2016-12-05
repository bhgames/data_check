from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Table, Enum, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, backref
import models.helpers.base
from models.helpers.timestamps_triggers import timestamps_triggers

Base = models.helpers.base.Base

from models.job_template import job_templates_schedules

class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    schedule_config = Column(JSONB, nullable=False)
    job_templates = relationship('JobTemplate', back_populates='schedules', secondary=job_templates_schedules)
    active = Column(Boolean, default=True, nullable=False)
    ENUMS=[]

timestamps_triggers(Schedule)

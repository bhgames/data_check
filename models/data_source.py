
from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from models.helpers.timestamps_triggers import timestamps_triggers
import enum
import re

ValidIpAddressRegex = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"

ValidHostnameRegex = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"

Base = declarative_base()

data_sources_job_templates = Table('data_sources_job_templates', Base.metadata,
    Column('data_source_id', Integer, ForeignKey('data_source_id.id')),
    Column('job_template_id', Integer, ForeignKey('job_template.id')))

class DataSourceType(enum.Enum):
    impala = "impala"

class DataSource(Base):
    __tablename__ = 'data_sources'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    data_source_type = Column(Enum(DataSourceType), nullable=False)
    host = Column(String, nullable=False)
    port = Column(String, nullable=False)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    job_templates = relationship('JobTemplate', back_populates="data_sources", secondary=data_sources_job_templates)

    @validates('port')
    def validate_port(self, key, port):
        assert re.match(r"^\d+$", port) != None
        return port

    @validates('host')
    def validate_host(self, key, host):
        assert (re.match(ValidIpAddressRegex, host) != None) or (re.match(ValidHostnameRegex, host) != None)
        return host


timestamps_triggers(DataSource)
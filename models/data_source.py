
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Table, DateTime
from sqlalchemy.orm import relationship, backref, validates
from sqlalchemy.dialects.postgresql import ARRAY
import models.helpers.base
from models.helpers.timestamps_triggers import timestamps_triggers
import enum
import re
from connections.impala_connection import ImpalaConnection

ValidIpAddressRegex = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"

ValidHostnameRegex = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"

Base = models.helpers.base.Base

from models.job_template import data_sources_job_templates

class DataSourceType(enum.Enum):
    impala = "impala"

class DataSource(Base):
    __tablename__ = 'data_source'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    data_source_type = Column(Enum(DataSourceType), nullable=False)
    host = Column(String, nullable=False)
    port = Column(String, nullable=False)
    user = Column(String, nullable=True)
    password = Column(String, nullable=True)
    schemas = Column(ARRAY(String), nullable=True)
    job_templates = relationship('JobTemplate', back_populates="data_sources", secondary=data_sources_job_templates)
    ENUMS = ["data_source_type"]

    @validates('port')
    def validate_port(self, key, port):
        assert re.match(r"^\d+$", str(port)) != None
        return port

    @validates('host')
    def validate_host(self, key, host):
        assert (re.match(ValidIpAddressRegex, host) != None) or (re.match(ValidHostnameRegex, host) != None)
        return host

    def config(self):
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password
        }

    def open_connection(self):
        self.db = ImpalaConnection(self.host, self.port, self.user, self.password)

    def close_connection(self):
        self.db.close()

    def tables(self):
        tables = []
        cur = self.db.cursor()

        for sch in self.schemas:
            cur.execute("use %s" % (sch))
            cur.execute("show tables")
            tables = tables + map(lambda r: sch + "." + r[0], cur.fetchall())


        return list(set(tables))


    def col_present(self, table, column):
        cur = self.db.cursor()

        cur.execute("SHOW COLUMN STATS " + table)

        for row in cur:
            if row[0] == column:
                return True 

        return False


    def count(self, table):
        cur = self.db.cursor()

        cur.execute("select count(*) from " + table)

        return cur.fetchone()[0]


timestamps_triggers(DataSource)
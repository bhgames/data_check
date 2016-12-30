
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Table, DateTime, Boolean
from sqlalchemy.orm import relationship, backref, validates
from sqlalchemy.orm.session import make_transient

from sqlalchemy.dialects.postgresql import ARRAY
import models.helpers.base
db_session = models.helpers.base.db_session
from models.helpers.timestamps_triggers import timestamps_triggers
import enum
import re
from connections.impala_connection import ImpalaConnection

ValidIpAddressRegex = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"

ValidHostnameRegex = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"

Base = models.helpers.base.Base

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

    # See JobTemplate for explanation
    read_only = Column(Boolean, default=False, nullable=False)
    parent_data_source_id = Column(Integer, nullable=True)

    ENUMS = ["data_source_type"]


    def become_read_only_clone(self):
        """
            Next time this object is saved it will be saved as a new entry,
            with read_only set to true, and parent id set to the cloner row.
        """
        
        self.parent_data_source_id = self.id
        self.read_only = True
        db_session.expunge(self)
        make_transient(self)
        self.id = None

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
        return self.db.tables(self.schemas)


    def col_present(self, table, column):
        return self.db.col_present(table, column)


    def count(self, table):
        return self.db.count(table)


timestamps_triggers(DataSource)
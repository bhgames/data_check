from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Table, DateTime, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.session import make_transient

import models.helpers.base
from models.helpers.timestamps_triggers import timestamps_triggers
from models.log import Log, HasLogs
from sqlalchemy.dialects.postgresql import JSONB
from copy import deepcopy
from models.data_source import DataSource
from models.job_run import JobRun, JobRunStatus
import datetime
now = datetime.datetime.now
from checks.date_gap_check import DateGapCheck
from checks.null_check import NullCheck
from checks.uniqueness_check import UniquenessCheck
from checks.column_comparison_check import ColumnComparisonCheck
from checks.id_gap_check import IdGapCheck
from checks.foreign_key_check import ForeignKeyCheck

import sys
from inflection import camelize

from models.rule import checks_rules

Base = models.helpers.base.Base
db_session = models.helpers.base.db_session

import enum
class CheckType(enum.Enum):
    uniqueness = "uniqueness"
    null = "null"
    date_gap = "date_gap"
    column_comparison = "column_comparison"
    id_gap = "id_gap"
    foreign_key = "foreign_key"


class Check(Base, HasLogs):
    __tablename__ = 'check'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    check_name = Column(String)
    check_type = Column(Enum(CheckType), nullable=False)
    check_metadata = Column(JSONB, nullable=False)

    # See Jobtemplate for explanation.
    read_only = Column(Boolean, default=False, nullable=False)
    parent_check_id = Column(Integer, nullable=True)

    rules = relationship("Rule", back_populates="checks", secondary=checks_rules)

    ENUMS = ["check_type"]


    def become_read_only_clone(self):
        """
            Next time this object is saved it will be saved as a new entry,
            with read_only set to true, and parent id set to the cloner row.
        """
        
        self.parent_check_id = self.id
        self.read_only = True
        db_session.expunge(self)
        make_transient(self)
        self.id = None


    def run(self, job_run, source, table):
        log = self.get_log(job_run=job_run)
        try:
            metadata = deepcopy(self.check_metadata)
            metadata["table"] = table.split(".")[1]
            metadata["schema"] = table.split(".")[0]
            metadata["log_metadata"] = { "table": metadata["table"], "schema": metadata["schema"], "source_id": source.id }
            metadata["config"] = source.config()
            metadata["log"] = log

            log.add_log("creation", "Begin %s Check of Source %s Table %s with Metadata %s" % (self.check_type.value, source.id, table, self.check_metadata), metadata["log_metadata"])
            db_session.add(job_run)

            if (job_run.status in [JobRunStatus.failed, JobRunStatus.cancelled, JobRunStatus.rejected]):
                log.add_log("cancelled", "Check cancelled due to Job Run Status of %s caused by some other worker." % (job_run.status))
            else:
                chk_class = eval(camelize(str(self.check_type.value)) + "Check")

                check = chk_class(metadata)
                check.run()
                log.add_log("finished", "Check Ended", metadata["log_metadata"])
        except Exception as e:
            print str(sys.exc_info())
            log.new_error_event()
            db_session.commit()
            raise

        db_session.commit()


timestamps_triggers(Check)

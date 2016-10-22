from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Table, DateTime
from sqlalchemy.orm import relationship, backref
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

import sys

Base = models.helpers.base.Base
Session = models.helpers.base.Session

import enum
class CheckType(enum.Enum):
    uniqueness = "Uniqueness"
    null = "Null"
    date_gap = "DateGap"

class Check(Base, HasLogs):
    __tablename__ = 'check'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    check_type = Column(Enum(CheckType), nullable=False)
    check_metadata = Column(JSONB, nullable=False)
    rule_id = Column(Integer, ForeignKey('rule.id'))
    rule = relationship("Rule", back_populates="checks")

    def run(self, job_run, source, table):
        session = Session.object_session(self)
        log = self.get_log(job_run=job_run)
        log.add_log("creation", "Begin %s Check of Source %s Table %s with Metadata %s" % (self.check_type.value, source.id, table, self.check_metadata))
        session.add(job_run)

        try:
            if (job_run.status in [JobRunStatus.failed, JobRunStatus.cancelled, JobRunStatus.rejected]):
                log.add_log("cancelled", "Check cancelled due to Job Run Status of %s caused by some other worker." % (job_run.status))
            else:
                chk_class = eval(str(self.check_type.value) + "Check")

                metadata = deepcopy(self.check_metadata)
                metadata["table"] = table.split(".")[1]
                metadata["schema"] = table.split(".")[0]
                metadata["config"] = source.config()
                metadata["log"] = log

                check = chk_class(metadata)
                check.run()
                log.add_log("finished", "Check Ended")
        except Exception as e:
            print str(sys.exc_info())
            log.new_error_event()
            job_run.set_failed()

        session.commit()


timestamps_triggers(Check)
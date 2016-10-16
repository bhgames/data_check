
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Table, DateTime
from sqlalchemy.orm import relationship, backref
import models.helpers.base
from models.helpers.timestamps_triggers import timestamps_triggers
from models.log import Log, HasLogs
from sqlalchemy.dialects.postgresql import JSONB
from models.checks import *
from copy import deepcopy
from models.data_source import DataSource
from models.job_run import JobRun, JobRunStatus
from datetime.datetime import now

Base = models.helpers.base.Base
Session = models.helpers.base.Session

from models.job_template import job_templates_rules

rules_tree = Table('rules_tree', Base.metadata,
    Column('parent_rule_id', Integer, ForeignKey('rule.id')),
    Column('child_rule_id', Integer, ForeignKey('rule.id')))

import enum
class RuleCondition(enum.Enum):
    if_col_present = "if_col_present"
    if_col_not_present = "if_col_not_present"
    if_table_name_matches = "if_table_name_matches"
    if_table_name_does_not_match = "if_table_name_does_not_match"
    if_record_count_above = "if_record_count_above"

class CheckType(enum.Enum):
    uniqueness = "Uniqeness"
    null = "Null"
    date_gap = "DateGap"

class Rule(Base, HasLogs):
    __tablename__ = 'rule'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    condition = Column(Enum(RuleCondition), nullable=False)
    conditional = Column(JSONB, default={}, nullable=False)
    checks = relationship('Check', back_populates="rule")
    job_templates = relationship('JobTemplate', back_populates="rules", secondary=job_templates_rules)
    children = relationship('Rule', back_populates="parent", secondary=rules_tree)
    parent = relationship('Rule', back_populates="children", secondary=rules_tree)

    def if_col_present(conditional, source, tables, log):
        column = conditional["column"]
        valid = [source, []]
        for table in tables:
            present = source.col_present(table, column)
            log.new_event("check", "Checking %s for column %s: %s" % (table, column, present))
            if present:
                valid[1].append(table)

        return valid

    def if_col_not_present(conditional, source, tables, log):
        return [source, tables - self.if_col_present(conditional, source, tables, log)[1]]

    def if_table_name_matches(conditional, source, tables, log):
        pattern = re.compile(conditional["pattern"])
        valid = [source, []]
        for table in tables:
            match = !!re.match(pattern, table)
            log.new_event("check", "Checking %s against match %s: %s" % (table, pattern, match))
            if match:
                valid[1].append(table)

        return valid


    def if_table_name_does_not_match(conditional, source, tables, log):
        return [source, self.if_table_name_matches(conditional, source, tables, log)[1]]


    def if_record_count_above(conditional, source, tables, log):
        count = conditional["count"]
        valid = [source, []]
        for table in tables:
            table_count = source.count(table)
            is_above = table_count > count
            log.new_event("check", "Checking %s count of %s against minimum requirement of %s: %s" % (table, table_count, count, is_above))
            if is_above:
                valid[1].append(table)

        return valid


    def all_tables_with_source(self):
        """
            Returns a list of lists, first entry is the data source, second is it's tables. This gets whittled down
            through filtering and passed along.
        """
        tables_and_sources = []
        [tables.append([source, source.tables()]) for source in self.job_template.data_sources]
        return tables_and_sources


    def run(self, job_run, checks_to_run, session, tables_and_sources = self.all_tables_with_source()):
        log = Log(job_run=job_run)
        log.add_log("creation", "Begin Rule Check")
        self.logs.append(log)
        session.add(log)

        try:
            log.new_event("check", "Checking %s condition for conditional %s" % (self.condition, self.conditional))

            # Whittle down the [source, [table1, table2...]] to same structure but only with tables matching condition.
            tables_and_sources_matching = [getattr(self, self.condition)(self.conditional, source_and_tables[0], source_and_tables[1], log) for source_and_tables in tables_and_sources]

            # Add tuples like (source, table, checkObj) to checks_to_run array by iterating over every source,
            # every table in that source, every check for that table. Triple generator magic.
            [[[checks_to_run.append((source_and_tables[0], table, check)) for check in self.checks] for table in source_and_tables[1]] for source_and_tables in tables_and_sources_matching]

            # Now allow any children rules to apply to tables that have been matched by this rule:
            [child.run(job_run, checks_to_run, session, tables_and_sources_matching) for child in self.children]
            log.new_event("finished", "Rule Check Ended")
        except Exception as e:
            print str(sys.exc_info())
            log.new_error_event()
            raise e


class Check(Base, HasLogs):
    __tablename__ = 'check'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    check_type = Column(Enum(CheckType), nullable=False)
    check_metadata = Column(JSONB, nullable=False)
    rule_id = Column(Integer, ForeignKey('rule.id'))
    rule = relationship("Rule", back_populates="checks")

    def run(job_run, source, table):
        session = Session()
        log = Log(job_run=job_run)
        log.add_log("creation", "Begin %s Check of Source %s Table %s for With Metadata %s" % (check_type, source.id, table, check_metadata))
        self.logs.append(log)
        session.add(log)
        session.add(job_run)

        try:
            if (job_run.status in [JobRunStatus.failed, JobRunStatus.cancelled, JobRunStatus.rejected]):
                log.add_log("cancelled", "Check cancelled due to Job Run Status of %s caused by some other worker." % (job_run.status))
            else:
                chk_class = eval(check_type + "Check")

                metadata = deepcopy(self.check_metadata)
                metadata["table"] = table.split(".")[1]
                metadata["schema"] = table.split(".")[0]
                metadata["config"] = source.config()
                metadata["log"] = log

                check = chk_class(metadata)
                check.run()
                log.new_event("finished", "Check Ended")
        except Exception as e:
            print str(sys.exc_info())
            log.new_error_event()
            job_run.set_failed()
            
        session.commit()

timestamps_triggers(Rule)
timestamps_triggers(Check)
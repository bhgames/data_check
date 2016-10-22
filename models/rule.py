
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Table, DateTime
from sqlalchemy.orm import relationship, backref
import models.helpers.base
from models.helpers.timestamps_triggers import timestamps_triggers
from models.log import Log, HasLogs
from sqlalchemy.dialects.postgresql import JSONB
from copy import deepcopy
from models.data_source import DataSource
import datetime
now = datetime.datetime.now

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


class Rule(Base, HasLogs):
    __tablename__ = 'rule'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    condition = Column(Enum(RuleCondition), nullable=False)
    conditional = Column(JSONB, default={}, nullable=False)
    checks = relationship('Check', back_populates="rule")
    job_templates = relationship('JobTemplate', back_populates="rules", secondary=job_templates_rules)
    children = relationship('Rule', back_populates="parent", secondary=rules_tree, 
                            primaryjoin= id == rules_tree.c.parent_rule_id,
                            secondaryjoin= id == rules_tree.c.child_rule_id)
    parent = relationship('Rule', back_populates="children", secondary=rules_tree, 
                            primaryjoin= id == rules_tree.c.child_rule_id,
                            secondaryjoin= id == rules_tree.c.parent_rule_id)

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
            match = True if re.match(pattern, table) else False
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


    def run(self, job_run, checks_to_run, tables_and_sources = None):
        session = Session.object_session(self)
        tables_and_sources = self.all_tables_with_source() if tables_and_sources == None else tables_and_sources
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
            [child.run(job_run, checks_to_run, tables_and_sources_matching) for child in self.children]
            log.new_event("finished", "Rule Check Ended")
        except Exception as e:
            print str(sys.exc_info())
            log.new_error_event()
            raise e


timestamps_triggers(Rule)

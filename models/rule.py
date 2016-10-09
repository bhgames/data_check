
from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from models.helpers.timestamps_triggers import timestamps_triggers
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

job_templates_rules = Table('job_templates_rules', Base.metadata,
    Column('rule_id', Integer, ForeignKey('rule.id')),
    Column('job_template_id', Integer, ForeignKey('job_template.id')))

rules_tree = Table('rules_tree', Base.metadata,
    Column('parent_rule_id', Integer, ForeignKey('rule.id')),
    Column('child_rule_id', Integer, ForeignKey('rule.id')))

import enum
class RuleCondition(enum.Enum):
    if_col_present = "if_col_present"
    if_col_not_present = "if_col_not_present"
    if_table_name_matches = "if_table_name_matches"
    if_table_name_does_not_match = "if_table_name_does_not_match"
    if_records_present = "if_records_present"
    if_record_count_above = "if_record_count_above"

class CheckType(enum.Enum):
    uniqueness = "uniqueness"
    not_null = "not_null"
    date_gap = "date_gap"

class Rule(Base):
    __tablename__ = 'rules'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    condition = Column(Enum(RuleCondition), nullable=False)
    conditional = Column(JSONB, default={}, nullable=False)
    checks = relationship('Check', back_populates="rule")
    job_templates = relationship('JobTemplate', back_populates="rules", secondary=job_templates_rules)
    children = relationship('Rule', back_populates="parent", secondary=rules_tree)
    parent = relationship('Rule', back_populates="children", secondary=rules_tree)

class Check(Base):
    __tablename__ = 'checks'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    check_type = Column(Enum(CheckType), nullable=False)
    check_metadata = Column(JSONB, nullable=False)
    rule_id = Column(Integer, ForeignKey('rule.id'))
    rule = relationship("Rule", back_populates="checks")

timestamps_triggers(Rule)
timestamps_triggers(Check)
from tests.base_test import BaseTest
from models.rule import Rule, RuleCondition
from models.job_run import JobRun, JobRunStatus
from models.job_template import JobTemplate, LogLevel
from models.check import Check, CheckType
import datetime
from functools import wraps
now = datetime.datetime.now
import models.helpers.base

db_session = models.helpers.base.db_session

class TestJobTemplate(BaseTest):


    def jt_clone(func):

        @wraps(func) # Wraps required for nosetests to see these wrapped tests, dunno why.
        def _decorator(self, *args, **kwargs):
            jt = JobTemplate(log_level = LogLevel.complete, name="Gob")
            r = Rule(
                condition=RuleCondition.if_col_present, 
                conditional={'column': 'id'}, 
                checks = [Check(check_type=CheckType.uniqueness, check_metadata={'column': 'id'})]
            )
            jt.data_sources.append(self.dummy_datasource())
            jt.rules.append(r)
            jt.become_read_only_clone()

        return _decorator


    @jt_clone
    def test_cloning_sets_id_null(self, jt):
        self.assertEquals(jt.id, None)


    @jt_clone
    def test_cloning_sets_read_only(self, jt):
        self.assertTrue(jt.read_only)

        
    @jt_clone
    def test_cloning_sets_parent_on_jt(self, jt):
        self.assertTrue(jt.parent_job_template_id != None)


    @jt_clone
    def test_cloning_sets_read_only_on_rule(self, jt):
        self.assertTrue(jt.rules[0].read_only)


    @jt_clone
    def test_cloning_sets_read_only_on_check(self, jt):
        self.assertTrue(jt.rules[0].checks[0].read_only)


    @jt_clone
    def test_cloning_sets_id_null_on_rule(self, jt):
        self.assertEquals(jt.rules[0].id, None)


    @jt_clone
    def test_cloning_sets_id_null_on_check(self, jt):
        self.assertEquals(jt.rules[0].checks[0].id, None)


    @jt_clone
    def test_cloning_sets_parent_on_rule(self, jt):
        self.assertTrue(jt.rules[0].parent_rule_id != None)


    @jt_clone
    def test_cloning_sets_parent_on_check(self, jt):
        self.assertTrue(jt.rules[0].checks[0].parent_check_id != None)
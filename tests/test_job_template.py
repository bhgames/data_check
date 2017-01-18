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

    @classmethod
    def sql(cls, type):
        return ""
    
    def jt_clone(func):

        @wraps(func) # Wraps required for nosetests to see these wrapped tests, dunno why.
        def _decorator(self, *args, **kwargs):
            jt = JobTemplate(log_level = LogLevel.complete, name="Gob")
            r = Rule(
                condition=RuleCondition.if_col_present, 
                conditional={'column': 'id'}, 
                checks = [Check(check_type=CheckType.uniqueness, check_metadata={'column': 'id'})],
                children = [Rule(condition=RuleCondition.if_col_present, conditional={'column': 'bloo'})]
            )
            jt.data_sources.append(self.dummy_datasource())
            jt.rules.append(r)
            db_session.add(jt)
            db_session.commit()

            jt.become_read_only_clone()
            func(self, jt)

        return _decorator


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
    def test_cloning_sets_read_only_on_ds(self, jt):
        self.assertTrue(jt.data_sources[0].read_only)


    @jt_clone
    def test_cloning_sets_parent_on_rule(self, jt):
        self.assertTrue(jt.rules[0].parent_rule_id != None)


    @jt_clone
    def test_cloning_sets_parent_on_check(self, jt):
        self.assertTrue(jt.rules[0].checks[0].parent_check_id != None)


    @jt_clone
    def test_cloning_sets_parent_on_ds(self, jt):
        self.assertTrue(jt.data_sources[0].parent_data_source_id != None)


    @jt_clone
    def test_cloning_with_save_makes_new_jt(self, jt):
        self.assertTrue(jt.id != None)
        self.assertNotEquals(jt.id, jt.parent_job_template_id)


    @jt_clone
    def test_cloning_with_save_makes_new_rule(self, jt):
        self.assertTrue(jt.rules[0].id != None)
        self.assertNotEquals(jt.rules[0].id, jt.rules[0].parent_rule_id)


    @jt_clone
    def test_cloning_with_save_makes_new_rule_child_rule(self, jt):
        self.assertTrue(jt.rules[0].children[0].id != None)
        self.assertNotEquals(jt.rules[0].children[0].id, jt.rules[0].children[0].parent_rule_id)


    @jt_clone
    def test_cloning_with_save_makes_new_check(self, jt):
        self.assertTrue(jt.rules[0].checks[0].id != None)
        self.assertNotEquals(jt.rules[0].checks[0].id, jt.rules[0].checks[0].parent_check_id)


    @jt_clone
    def test_cloning_with_save_makes_new_data_source(self, jt):
        self.assertTrue(jt.data_sources[0].id != None)
        self.assertNotEquals(jt.data_sources[0].id, jt.data_sources[0].parent_data_source_id)


    @jt_clone
    def test_cloning_creates_duplicates_in_db(self, jt):
        self.assertEquals(len(db_session.query(JobTemplate).all()), 2)

    @jt_clone
    def test_cloning_creates_one_ro_and_leaves_one_real(self, jt):

        self.assertEquals(db_session.query(JobTemplate).filter(JobTemplate.read_only==True).count(), 1)
        self.assertEquals(db_session.query(JobTemplate).filter(JobTemplate.read_only==False, JobTemplate.parent_job_template_id==None).count(), 1)
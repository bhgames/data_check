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

class TestJobRun(BaseTest):


    def create_and_run_no_rules(func):

        @wraps(func) # Wraps required for nosetests to see these wrapped tests, dunno why.
        def _decorator(self, *args, **kwargs):
            jt = JobTemplate(log_level = LogLevel.complete, name="Gob")
            self.s.add(jt)

            # Actually runs the job
            jr = JobRun.create_job_run(jt)

            jr = self.s.query(JobRun).get(jr.id)
            jt = self.s.query(JobTemplate).get(jt.id)
            func(self, jt, jr)

        return _decorator


    def create_and_run_with_rule(func):

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
            self.s.add_all([jt, r])
            # Actually runs the job
            jr = JobRun.create_job_run(jt)
            # Refresh Obj from DB
            jr = self.s.query(JobRun).get(jr.id)
            jt = self.s.query(JobTemplate).get(jt.id)
            func(self, jt, jr)

        return _decorator

    @create_and_run_no_rules
    def test_create_job_run_creates(self, jt, jr):
        self.assertTrue(jr.id != None)


    @create_and_run_no_rules
    def test_create_job_run_sets_run_at(self, jt, jr):
        self.assertTrue(jr.run_at != None)


    @create_and_run_no_rules
    def test_create_job_run_sets_scheduled_at(self, jt, jr):
        self.assertTrue(jr.scheduled_at != None)


    @create_and_run_no_rules
    def test_create_job_run_schedules_and_finishes(self, jt, jr):
        self.assertTrue(JobRunStatus.finished, jr.status)


    @create_and_run_no_rules
    def test_create_job_run_schedules_and_logs(self, jt, jr):
        self.assertEqual(map(lambda l: l["event"], jr.logs[0].log), ["started", "finished"])


    @create_and_run_with_rule
    def test_create_job_run_has_logs_for_rule_separated_from_job_run_itself(self, jt, jr):
        self.assertNotEqual(jr.get_log(job_run=jr).id, jt.rules[0].get_log(job_run=jr).id)


    @create_and_run_with_rule
    def test_create_job_run_logs_for_rule_different_than_logs_for_run(self, jt, jr):
        self.assertNotEqual(jr.get_log(job_run=jr).log[0], jt.rules[0].get_log(job_run=jr).log[0])


    @create_and_run_with_rule
    def test_create_job_run_creates_checks(self, jt, jr):
        self.assertEqual("finished", jt.rules[0].checks[0].get_log(job_run=jr).log[-1]['event'])


    @create_and_run_no_rules
    def test_set_failed_sets_failed_at(self, jt, jr):
        jr.set_failed()
        self.assertTrue(jr.failed_at != None)


    @create_and_run_no_rules
    def test_set_failed_sets_failed_status(self, jt, jr):
        jr.set_failed()
        self.assertEqual(jr.status, JobRunStatus.failed)


    @create_and_run_no_rules
    def test_set_failed_sets_failed_event(self, jt, jr):
        jr.set_failed()
        self.assertEqual('failed', jr.get_log(job_run=jr).log[-1]['event'])


    @create_and_run_no_rules
    def test_set_failed_sets_finished_at(self, jt, jr):
        jr.set_finished()
        self.assertTrue(jr.finished_at != None)


    @create_and_run_no_rules
    def test_set_failed_sets_finished_status(self, jt, jr):
        jr.set_finished()
        self.assertEqual(jr.status, JobRunStatus.finished)


if __name__ == '__main__':
    unittest.main()
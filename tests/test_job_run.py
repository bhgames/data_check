from tests.base_test import BaseTest
from models.rule import Rule, RuleCondition
from models.job_run import JobRun, JobRunStatus
from models.job_template import JobTemplate, LogLevel
from models.check import Check, CheckType
import datetime
from functools import wraps
now = datetime.datetime.now
import models.helpers.base

Session = models.helpers.base.Session

class TestJobRun(BaseTest):


    def create_and_run_no_rules(func):

        @wraps(func) # Wraps required for nosetests to see these wrapped tests, dunno why.
        def _decorator(self, *args, **kwargs):
            jt = JobTemplate(log_level = LogLevel.complete, name="Gob")
            self.s.add(jt)
            # Actually runs the job
            jr = JobRun.create_job_run(self.s, jt, now())
            self.s.close()
            self.s = Session()
            jr = self.s.query(JobRun).get(jr.id)
            func(self, jt, jr)

        return _decorator


    def create_and_run_with_rule(func):

        @wraps(func) # Wraps required for nosetests to see these wrapped tests, dunno why.
        def _decorator(self, *args, **kwargs):
            jt = JobTemplate(log_level = LogLevel.complete, name="Gob")
            self.s.add(jt)
            # Actually runs the job
            jr = JobRun.create_job_run(self.s, jt, now())
            self.s.close()
            self.s = Session()
            jr = self.s.query(JobRun).get(jr.id)
            func(self, jt, jr)

        return _decorator

    @create_and_run_no_rules
    def test_create_job_run_creates(self, jt, jr):
        self.assertTrue(jr.id != None)


    @create_and_run_no_rules
    def test_create_job_run_schedules_and_finishes(self, jt, jr):
        self.assertTrue(JobRunStatus.finished, jr.status)


    @create_and_run_no_rules
    def test_create_job_run_schedules_and_logs(self, jt, jr):
        print jr.get_log(job_run=jr).log
        self.assertEqual(map(lambda l: l["event"], jr.logs[0].log), ["started", "finished"])



if __name__ == '__main__':
    unittest.main()
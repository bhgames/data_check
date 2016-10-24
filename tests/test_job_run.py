from tests.base_test import BaseTest
from models.rule import Rule, RuleCondition
from models.job_run import JobRun
from models.job_template import JobTemplate, LogLevel
from models.check import Check, CheckType
import datetime
from functools import wraps
now = datetime.datetime.now


class TestJobRun(BaseTest):


    def test_create_job_run_creates(self):
        jt = JobTemplate(log_level = LogLevel.complete, name="Gob")
        self.s.add(jt)
        JobRun.create_job_run(self.s, jt, now())

        jr = self.s.query(JobRun).filter_by(job_template_id=jt.id).first()
        self.assertTrue(jr.id != None)

    def test_create_job_run_schedules(self):
        jt = JobTemplate(log_level = LogLevel.complete, name="Gob")
        self.s.add(jt)
        # Actually runs the job
        result = JobRun.create_job_run(self.s, jt, now()).get()

        

if __name__ == '__main__':
    unittest.main()
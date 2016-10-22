from tests.base_test import BaseTest
from models.check import Check, CheckType
from models.job_run import JobRun, JobRunStatus
from models.data_source import DataSource, DataSourceType
import datetime
now = datetime.datetime.now


class TestCheck(BaseTest):

    def assert_event(self, job_run_status, event_type, event_index, table='test.test_uniqueness_success'):
        c = Check(check_type=CheckType.uniqueness, check_metadata={'column': 'id'})
        j = JobRun(status=job_run_status, scheduled_at=now())
        d = self.dummy_datasource()
        
        self.s.add_all([c, j, d])
        self.s.commit()

        c.run(j, d, table)

        l = c.logs[0]

        event = l.log[event_index]

        print event
        self.assertEqual(event['event'], event_type)


    def test_job_run_in_fail_status_logs_cancelled_event(self):
        self.assert_event(JobRunStatus.failed, "cancelled", -1)


    def test_job_run_in_cancelled_status_logs_cancelled_event(self):
        self.assert_event(JobRunStatus.cancelled, "cancelled", -1)


    def test_job_run_in_rejected_status_logs_cancelled_event(self):
        self.assert_event(JobRunStatus.rejected, "cancelled", -1)


    def test_job_run_successful_logs_finished_event(self):
        self.assert_event(JobRunStatus.running, "finished", -1)


    def test_runs_actual_check(self):
        self.assert_event(JobRunStatus.running, "collection", 1)


    def test_gets_check_result(self):
        self.assert_event(JobRunStatus.running, "result", 2)


    def test_gets_check_pass(self):
        self.assert_event(JobRunStatus.running, "check_succeeded", 3)

    def test_gets_check_fail(self):
        self.assert_event(JobRunStatus.running, "check_failed", 3, 'test.test_uniqueness_fail')

if __name__ == '__main__':
    unittest.main()
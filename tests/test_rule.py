from tests.base_test import BaseTest
from models.rule import Rule, RuleCondition
from models.job_run import JobRun, JobRunStatus
from models.job_template import JobTemplate
from models.check import Check, CheckType
import datetime
from functools import wraps
now = datetime.datetime.now


class TestRule(BaseTest):
    @classmethod
    def sql(cls, type):
        return """
             CREATE TABLE test.test_uniqueness_fail (                            
               id INT                                                            
             );


            insert into test.test_uniqueness_fail(id) values
              (1), (2), (1);

            CREATE TABLE test.test_uniqueness_success (                            
               id INT                                                               
             );

            insert into test.test_uniqueness_success(id) values
              (1), (2);

            CREATE TABLE test.test_date_gap_success (                            
               updated_at TIMESTAMP                                               
             );


            insert into test.test_date_gap_success(updated_at) values
              ('2015-01-02 00:00:00'),
              ('2015-01-04 00:00:00'),
              ('2015-01-03 00:00:00'),
              ('2015-01-02 00:00:00'),
              ('2015-01-01 00:00:00');

        """
    

    def dummy_rule(func):

        @wraps(func) # Wraps required for nosetests to see these wrapped tests, dunno why.
        def _decorator(self, *args, **kwargs):
            r = Rule(
                condition=RuleCondition.if_col_present, 
                conditional={'column': 'id'}, 
                checks = [Check(check_type=CheckType.uniqueness, check_metadata={'column': 'id'})]
            )
            d = self.dummy_datasource()
            jr = self.dummy_job_run(d)
            self.s.add_all([r, d, jr])
            d.open_connection()
            func(self, r, d, jr)
            d.close_connection()

        return _decorator

    def dummy_job_run(self, d):
        return JobRun(job_template=JobTemplate(data_sources=[d], name="B"), scheduled_at=now(), status=JobRunStatus.running)


    @dummy_rule
    def test_if_col_present_is_present(self, r, d, jr):
        self.assertEqual([d, ['test.test_uniqueness_success']], r.if_col_present({'column': 'id'}, d, ['test.test_uniqueness_success'], jr))


    @dummy_rule
    def test_if_col_present_is_not_present(self, r, d, jr):
        self.assertEqual([d, []], r.if_col_present({'column': 'idx'}, d, ['test.test_uniqueness_success'], jr))


    @dummy_rule
    def test_if_col_not_present_is_not_present(self, r, d, jr):
        self.assertEqual([d, ['test.test_uniqueness_success']], r.if_col_not_present({'column': 'idx'}, d, ['test.test_uniqueness_success'], jr))


    @dummy_rule
    def test_if_col_not_present_is_present(self, r, d, jr):
        self.assertEqual([d, []], r.if_col_not_present({'column': 'id'}, d, ['test.test_uniqueness_success'], jr))


    @dummy_rule
    def test_if_table_name_matches_actually_matches(self, r, d, jr):
        self.assertEqual([d, ['test.test_uniqueness_success']], r.if_table_name_matches({'pattern': 'test.*'}, d, ['test.test_uniqueness_success'], jr))


    @dummy_rule
    def test_if_table_name_matches_doesnt_actually_match(self, r, d, jr):
        self.assertEqual([d, []], r.if_table_name_matches({'pattern': 'testx_.*'}, d, ['test.test_uniqueness_success'], jr))


    @dummy_rule
    def test_if_table_name_does_not_match_actually_matches(self, r, d, jr):
        self.assertEqual([d, []], r.if_table_name_does_not_match({'pattern': 'test.*'}, d, ['test.test_uniqueness_success'], jr))


    @dummy_rule
    def test_if_table_name_does_not_match_doesnt_actually_match(self, r, d, jr):
        self.assertEqual([d, ['test.test_uniqueness_success']], r.if_table_name_does_not_match({'pattern': 'testx_.*'}, d, ['test.test_uniqueness_success'], jr))


    @dummy_rule
    def test_if_record_count_above_is_above(self, r, d, jr):
        self.assertEqual([d, ['test.test_uniqueness_success']], r.if_record_count_above({'count': 1}, d, ['test.test_uniqueness_success'], jr))


    @dummy_rule
    def test_if_record_count_above_is_not_above(self, r, d, jr):
        self.assertEqual([d, []], r.if_record_count_above({'count': 100}, d, ['test.test_uniqueness_success'], jr))


    @dummy_rule
    def test_all_tables_with_source_returns_proper_source(self, r, d, jr):
        job_template = JobTemplate(data_sources=[d], name="B")
        result = r.all_tables_with_source(jr)
        self.assertEqual(d, result[0][0])


    @dummy_rule
    def test_all_tables_with_source_returns_proper_tables(self, r, d, jr):
        job_template = JobTemplate(data_sources=[d], name="B")
        result = r.all_tables_with_source(jr)
        self.assertTrue('test.test_uniqueness_success' in result[0][1])
        self.assertTrue('test.test_uniqueness_fail' in result[0][1])


    @dummy_rule
    def test_rule_runs_logs_creation(self, r, d, jr):
        r.run(jr, [])
        self.assertEqual('creation', r.get_log(job_run=jr).log[0]['event'])


    @dummy_rule
    def test_rule_runs_logs_finished(self, r, d, jr):
        r.run(jr, [])
        self.assertEqual('finished', r.get_log(job_run=jr).log[-1]['event'])


    @dummy_rule
    def test_rule_runs_logs_check(self, r, d, jr):
        r.run(jr, [])
        self.assertEqual('check', r.get_log(job_run=jr).log[1]['event'])


    def run_rule(self, r, d, jr):
        checks_to_run = []
        job_template = jr.job_template
        checks = r.run(jr, checks_to_run)
        tables = r.all_tables_with_source(jr)[0][1]
        return checks_to_run


    @dummy_rule
    def test_rule_runs_returns_proper_check(self, r, d, jr):
        checks_to_run = self.run_rule(r,d, jr)
        self.assertTrue((d, 'test.test_uniqueness_fail', r.checks[0]) in checks_to_run)


    @dummy_rule
    def test_rule_runs_returns_proper_number_of_checks(self, r, d, jr):
        checks_to_run = self.run_rule(r,d, jr)
        self.assertEqual(2, len(checks_to_run))


    @dummy_rule
    def test_rule_runs_doesnt_return_improper_checks(self, r, d, jr):
        checks_to_run = self.run_rule(r,d, jr)
        # Only tables with id present(the rule in dummy rule) are the uniqueness fail/succ tables, null check tables and id gap table.
        self.assertFalse((d, 'test.test_date_gap_success', r.checks[0]) in checks_to_run)


    @dummy_rule
    def test_rule_runs_include_children_rule_checks(self, r, d, jr):
        r.children.append(Rule(
            condition=RuleCondition.if_table_name_matches, 
            conditional={'pattern': 'test_uniqueness'}, 
            checks = [Check(check_type=CheckType.null, check_metadata={'column': 'id'})]
        ))

        checks_to_run = self.run_rule(r,d, jr)

        self.assertTrue((d, 'test.test_uniqueness_success', r.children[0].checks[0]) in checks_to_run)





if __name__ == '__main__':
    unittest.main()
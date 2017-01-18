from tests.base_test import BaseTest

from checks.date_gap_check import DateGapCheck

from ddt import ddt, data

@ddt
class TestDateGapCheck(BaseTest):
    @classmethod
    def sql(cls, type):
        string = """

            CREATE TABLE test.test_date_gap_fail (                            
               updated_at TIMESTAMP                                            
             );


            insert into test.test_date_gap_fail(updated_at) values
              ('2015-02-02 00:00:00'), 
              ('2015-02-06 00:00:00'), 
              ('2015-02-03 00:00:00'), 
              ('2015-01-01 00:00:00'), 
              ('2015-01-03 00:00:00');

            CREATE TABLE test.test_date_gap_fail_str_updated_at (                            
               updated_at STRING                                                                 
             );

            insert into test.test_date_gap_fail_str_updated_at(updated_at) values
              ('2015-02-09 00:02:00'), 
              ('2015-02-12 00:02:00'), 
              ('2015-02-13 00:02:00'), 
              ('2015-02-10 00:02:00');

            CREATE TABLE test.test_date_gap_success (                            
               updated_at TIMESTAMP                                               
             );


            insert into test.test_date_gap_success(updated_at) values
              ('2015-01-02 00:00:00'),
              ('2015-01-04 00:00:00'),
              ('2015-01-03 00:00:00'),
              ('2015-01-02 00:00:00'),
              ('2015-01-01 00:00:00');

            CREATE TABLE test.test_date_gap_success_same_day_events (                            
               updated_at TIMESTAMP                                                               
             );

            insert into test.test_date_gap_success_same_day_events(updated_at) values
              ('2015-02-06 00:02:00'),
              ('2015-02-07 00:02:00'),
              ('2015-02-06 00:00:00');


            CREATE TABLE test.test_date_gap_success_str_updated_at (                            
               updated_at STRING                                                                    
             );

            insert into test.test_date_gap_success_str_updated_at(updated_at) values
              ('2015-02-09 00:02:00'),
              ('2015-02-10 00:02:00'),
              ('2015-02-11 00:03:00'),
              ('2015-02-11 00:02:00');

            """

        if type == "postgres":
            string = string.replace("STRING", "varchar(50)")

        return string


    @data("impala", "postgres")
    def test_date_gap_same_day_success(self, type):
        u = DateGapCheck({"table": "test_date_gap_success_same_day_events", "schema": "test", "column": "updated_at", "config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)


    @data("impala", "postgres")
    def test_date_gap_success_on_string_field(self, type):
        u = DateGapCheck({"table": "test_date_gap_success_str_updated_at", "schema": "test", "column": "updated_at", "config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)


    @data("impala", "postgres")
    def test_date_gap_failure_on_string_field(self, type):
        u = DateGapCheck({"table": "test_date_gap_fail_str_updated_at", "schema": "test", "column": "updated_at", "config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 1)
        self.assertTrue(u.failed)
        self.assertEqual(str(u.failed_rows.iloc[0].gap_start), '2015-02-10 00:02:00')
        self.assertEqual(str(u.failed_rows.iloc[0].gap_end), '2015-02-12 00:02:00')


    @data("impala", "postgres")
    def test_date_gap_failure(self, type):
        u = DateGapCheck({"table": "test_date_gap_fail", "schema": "test", "column": "updated_at", "config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 3)
        self.assertTrue(u.failed)
        self.assertEqual(str(u.failed_rows.iloc[0].gap_start), '2015-01-01 00:00:00')
        self.assertEqual(str(u.failed_rows.iloc[0].gap_end), '2015-01-03 00:00:00')


    @data("impala", "postgres")
    def test_date_gap_success(self, type):
        u = DateGapCheck({"table": "test_date_gap_success", "schema": "test", "column": "updated_at", "config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

if __name__ == '__main__':
    unittest.main()
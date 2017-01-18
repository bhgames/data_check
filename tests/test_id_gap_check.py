from tests.base_test import BaseTest

from checks.id_gap_check import IdGapCheck

from ddt import ddt, data

@ddt
class TestNullCheck(BaseTest):

    @classmethod
    def sql(cls, type):
        return """

            CREATE TABLE test.test_id_gap (                            
               id INT                                                   
             );

            insert into test.test_id_gap(id) values
              (1), (5);

        """

    @data("impala", "postgres")
    def test_id_gap_failure(self, type):
        u = IdGapCheck({"table": "test_id_gap", "schema": "test", "column": "id", "threshold": "3", "config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 1)
        self.assertTrue(u.failed)
        self.assertEqual(u.failed_rows.iloc[0].gap_start, 1)
        self.assertEqual(u.failed_rows.iloc[0].gap_end, 5)

    @data("impala", "postgres")
    def test_id_gap_success(self, type):
        u = IdGapCheck({"table": "test_id_gap", "schema": "test", "column": "id", "threshold": "30", "config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

if __name__ == '__main__':
    unittest.main()
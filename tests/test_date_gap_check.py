from tests.base_test import BaseTest

from checks.date_gap_check import DateGapCheck

class TestDateGapCheck(BaseTest):

    def test_date_gap_failure(self):
        u = DateGapCheck({"table": "test_date_gap_fail", "schema": "test", "column": "updated_at", "config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 2)
        self.assertTrue(u.failed)
        self.assertEqual(str(u.failed_rows.iloc[0].gap_start), '2015-01-03 00:00:00')
        self.assertEqual(str(u.failed_rows.iloc[0].gap_end), '2015-02-02 00:00:00')

    def test_date_gap_success(self):
        u = DateGapCheck({"table": "test_date_gap_success", "schema": "test", "column": "updated_at", "config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

if __name__ == '__main__':
    unittest.main()
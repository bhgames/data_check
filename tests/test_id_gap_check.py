from tests.base_test import BaseTest

from checks.id_gap_check import IdGapCheck

class TestNullCheck(BaseTest):

    def test_id_gap_failure(self):
        u = IdGapCheck({"table": "test_id_gap", "schema": "test", "column": "id", "threshold": "3", "config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 1)
        self.assertTrue(u.failed)
        self.assertEqual(u.failed_rows.iloc[0].gap_start, 1)
        self.assertEqual(u.failed_rows.iloc[0].gap_end, 5)

    def test_id_gap_success(self):
        u = IdGapCheck({"table": "test_id_gap", "schema": "test", "column": "id", "threshold": "30", "config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

if __name__ == '__main__':
    unittest.main()
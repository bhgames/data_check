from tests.base_test import BaseTest

from checks.column_comparison_check import ColumnComparisonCheck

class TestColumnComparisonCheck(BaseTest):

    def test_col_comparison_failure(self):
        u = ColumnComparisonCheck({"table": "test_col_comparison_fail", "schema": "test", "expression": "x != y", "config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 1)
        self.assertTrue(u.failed)
        self.assertEqual(u.failed_rows.iloc[0].x, 1)
        self.assertEqual(u.failed_rows.iloc[0].y, 1)

    def test_col_comparison_success(self):
        u = ColumnComparisonCheck({"table": "test_col_comparison_success", "schema": "test", "expression": "x != y", "config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

if __name__ == '__main__':
    unittest.main()
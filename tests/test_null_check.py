from tests.base_test import BaseTest

from checks.null_check import NullCheck

class TestNullCheck(BaseTest):

    def test_null_failure(self):
        u = NullCheck({"table": "test_null_fail", "schema": "test", "column": "status", "config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 1)
        self.assertTrue(u.failed)
        self.assertEqual(u.failed_rows.iloc[0].id, 1)

    def test_null_success(self):
        u = NullCheck({"table": "test_null_success", "schema": "test", "column": "status", "config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

if __name__ == '__main__':
    unittest.main()
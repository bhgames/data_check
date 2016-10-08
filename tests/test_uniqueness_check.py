from tests.base_test import BaseTest

from checks.uniqueness_check import UniquenessCheck

class TestUniquenessCheck(BaseTest):

    def test_uniqueness_failure(self):
        u = UniquenessCheck({"table": "test_uniqueness_fail", "schema": "test", "column": "id", "config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 1)
        self.assertTrue(u.failed)
        self.assertEqual(u.failed_rows.iloc[0].id, 1)

    def test_uniqueness_success(self):
        u = UniquenessCheck({"table": "test_uniqueness_success", "schema": "test", "column": "id", "config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

if __name__ == '__main__':
    unittest.main()
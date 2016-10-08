import unittest

from checks.uniqueness_check import UniquenessCheck

class TestUniquenessCheck(unittest.TestCase):

    def config(self):
        return {
            "host": "localhost",
            "port": 21050
        }

    def test_uniqueness_failure(self):
        u = UniquenessCheck({"table": "test.test_uniqueness_fail", "column": "id", "config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 1)
        self.assertTrue(u.failed)
        self.assertEqual(u.failed_rows.iloc[0].id, 1)

    def test_uniqueness_success(self):
        u = UniquenessCheck({"table": "test.test_uniqueness_success", "column": "id", "config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

if __name__ == '__main__':
    unittest.main()
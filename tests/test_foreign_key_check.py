from tests.base_test import BaseTest

from checks.foreign_key_check import ForeignKeyCheck

class TestForeignKeyCheck(BaseTest):

    def test_foreign_key_failure_on_nonexistent_table(self):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_single_fk_fail_on_bad_table", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^id$" ,"config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertTrue(u.failed)


    def test_foreign_key_failure_on_single_column(self):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_single_fk_fail", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^id$" ,"config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 1)
        self.assertTrue(u.failed)
        self.assertEqual(u.failed_rows.iloc[0].id, 2)


    def test_foreign_key_failure_on_single_column_due_to_no_group_match(self):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_single_fk_fail", "schema": "test", "fk_col_pattern": ".*_id$", "fk_table_id_pattern": "^id$" ,"config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertTrue(u.failed)


    def test_foreign_key_failure_on_single_column_due_to_bad_fk_id_pattern(self):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_single_fk_fail", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^idx$" ,"config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertTrue(u.failed)


    def test_foreign_key_singularize(self):
        u = ForeignKeyCheck({"singularize": True, "table": "test_fk_singularize", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^id$" ,"config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)


    def test_foreign_key_pluralize(self):
        u = ForeignKeyCheck({"pluralize": True, "table": "test_fk_pluralize", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^id$" ,"config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)


    def test_foreign_key_success_on_single_column(self):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_single_fk_success", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^id$" ,"config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)


    def test_foreign_key_success_on_single_column_due_to_no_matches(self):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_single_fk_success", "schema": "test", "fk_col_pattern": "(.*)_idx$", "fk_table_id_pattern": "^id$" ,"config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)


    def test_foreign_key_success_on_double_column(self):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_double_fk_success", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^id$" ,"config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)


    def test_foreign_key_fail_on_double_column(self):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_double_fk_fail", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^id$" ,"config": self.config()})
        u.run()

        self.assertEqual(len(u.failed_rows), 1)
        self.assertTrue(u.failed)
        self.assertEqual(u.failed_rows.iloc[0].id, 1)

if __name__ == '__main__':
    unittest.main()
from tests.base_test import BaseTest

from checks.foreign_key_check import ForeignKeyCheck

from ddt import ddt, data

@ddt
class TestForeignKeyCheck(BaseTest):
    @classmethod
    def sql(cls, type):
        return """

            --- PK Single FK Success

            CREATE TABLE test.test_fk_primary_table_single_fk_success (                            
               id INT,
               test_fk_secondary_table_single_fk_success_id INT                            
             );

            insert into test.test_fk_primary_table_single_fk_success(id, test_fk_secondary_table_single_fk_success_id) values
              (1,1), (2,2), (3, NULL);


            CREATE TABLE test.test_fk_secondary_table_single_fk_success (                            
               id INT
             );

            insert into test.test_fk_secondary_table_single_fk_success(id) values
              (1), (2);


            -- Single FK Success w/ Pluralize

            CREATE TABLE test.test_fk_pluralize (                            
               id INT,
               test_fk_secondary_table_pluralize_id INT                            
             );

            insert into test.test_fk_pluralize(id, test_fk_secondary_table_pluralize_id) values
              (1,1), (2,2), (3, NULL);


            CREATE TABLE test.test_fk_secondary_table_pluralizes (                            
               id INT
             );

            insert into test.test_fk_secondary_table_pluralizes(id) values
              (1), (2);


            -- FK Singularize


            CREATE TABLE test.test_fk_singularize (                            
               id INT,
               test_fk_secondary_table_singularizes_id INT                            
             );

            insert into test.test_fk_singularize(id, test_fk_secondary_table_singularizes_id) values
              (1,1), (2,2), (3, NULL);


            CREATE TABLE test.test_fk_secondary_table_singularize (                            
               id INT
             );

            insert into test.test_fk_secondary_table_singularize(id) values
              (1), (2);


            -- Single FK Fail

            CREATE TABLE test.test_fk_primary_table_single_fk_fail (                            
               id INT,
               test_fk_secondary_table_single_fk_fail_id INT                            
             );

            insert into test.test_fk_primary_table_single_fk_fail(id, test_fk_secondary_table_single_fk_fail_id) values
              (1,1), (2,3);


            CREATE TABLE test.test_fk_secondary_table_single_fk_fail (                            
               id INT
             );

            insert into test.test_fk_secondary_table_single_fk_fail(id) values
              (1), (2);


            -- Single FK Fail on non-existent FK table


            CREATE TABLE test.test_fk_primary_table_single_fk_fail_on_bad_table (                            
               id INT,
               test_fk_secondary_table_single_fk_fail1_id INT                            
             );


            -- Double FK Success

            CREATE TABLE test.test_fk_primary_table_double_fk_success (                            
               id INT,
               test_fk_secondary_table_double_fk_success_id INT,
               test_fk_tertiary_table_double_fk_success_id INT                            
             );

            insert into test.test_fk_primary_table_double_fk_success(id, test_fk_secondary_table_double_fk_success_id, test_fk_tertiary_table_double_fk_success_id) values
              (1,1,1), (2,2,2);


            CREATE TABLE test.test_fk_secondary_table_double_fk_success (                            
               id INT
             );

            insert into test.test_fk_secondary_table_double_fk_success(id) values
              (1), (2);


            CREATE TABLE test.test_fk_tertiary_table_double_fk_success (                            
               id INT
             );

            insert into test.test_fk_tertiary_table_double_fk_success(id) values
              (1), (2);


            -- Double FK Fail

            CREATE TABLE test.test_fk_primary_table_double_fk_fail (                            
               id INT,
               test_fk_secondary_table_double_fk_fail_id INT,
               test_fk_tertiary_table_double_fk_fail_id INT                            
             );

            insert into test.test_fk_primary_table_double_fk_fail(id, test_fk_secondary_table_double_fk_fail_id, test_fk_tertiary_table_double_fk_fail_id) values
              (1,3,1), (2,2,2);


            CREATE TABLE test.test_fk_secondary_table_double_fk_fail (                            
               id INT
             );

            insert into test.test_fk_secondary_table_double_fk_fail(id) values
              (1), (2);


            CREATE TABLE test.test_fk_tertiary_table_double_fk_fail (                            
               id INT
             );

            insert into test.test_fk_tertiary_table_double_fk_fail(id) values
              (1), (2);


        """
    @data("impala", "postgres")    
    def test_foreign_key_failure_on_nonexistent_table(self, type):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_single_fk_fail_on_bad_table", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^id$" ,"config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertTrue(u.failed)

    @data("impala", "postgres")
    def test_foreign_key_failure_on_single_column(self, type):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_single_fk_fail", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^id$" ,"config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 1)
        self.assertTrue(u.failed)
        self.assertEqual(u.failed_rows.iloc[0].id, 2)

    @data("impala", "postgres")
    def test_foreign_key_failure_on_single_column_due_to_no_group_match(self, type):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_single_fk_fail", "schema": "test", "fk_col_pattern": ".*_id$", "fk_table_id_pattern": "^id$" ,"config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertTrue(u.failed)

    @data("impala", "postgres")
    def test_foreign_key_failure_on_single_column_due_to_bad_fk_id_pattern(self, type):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_single_fk_fail", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^idx$" ,"config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertTrue(u.failed)

    @data("impala", "postgres")
    def test_foreign_key_singularize(self, type):
        u = ForeignKeyCheck({"singularize": True, "table": "test_fk_singularize", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^id$" ,"config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

    @data("impala", "postgres")
    def test_foreign_key_pluralize(self, type):
        u = ForeignKeyCheck({"pluralize": True, "table": "test_fk_pluralize", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^id$" ,"config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

    @data("impala", "postgres")
    def test_foreign_key_success_on_single_column(self, type):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_single_fk_success", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^id$" ,"config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

    @data("impala", "postgres")
    def test_foreign_key_success_on_single_column_due_to_no_matches(self, type):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_single_fk_success", "schema": "test", "fk_col_pattern": "(.*)_idx$", "fk_table_id_pattern": "^id$" ,"config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

    @data("impala", "postgres")
    def test_foreign_key_success_on_double_column(self, type):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_double_fk_success", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^id$" ,"config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

    @data("impala", "postgres")
    def test_foreign_key_fail_on_double_column(self, type):
        u = ForeignKeyCheck({"table": "test_fk_primary_table_double_fk_fail", "schema": "test", "fk_col_pattern": "(.*)_id$", "fk_table_id_pattern": "^id$" ,"config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 1)
        self.assertTrue(u.failed)
        self.assertEqual(u.failed_rows.iloc[0].id, 1)

if __name__ == '__main__':
    unittest.main()
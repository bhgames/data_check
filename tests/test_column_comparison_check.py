from tests.base_test import BaseTest

from checks.column_comparison_check import ColumnComparisonCheck

from ddt import ddt, data

@ddt
class TestColumnComparisonCheck(BaseTest):

    @classmethod
    def sql(cls, type):
        return """
            CREATE TABLE test.test_col_comparison_fail (                            
               x INT,                                                                
               y INT                                                                 
             );

            insert into test.test_col_comparison_fail(x,y) values (1,1);


             CREATE TABLE test.test_col_comparison_success (                            
               x INT,                                                                   
               y INT                                                                    
             );

            insert into test.test_col_comparison_success(x,y) values (1,2);

        """


    @data("impala", "postgres")
    def test_col_comparison_failure(self, type):
        u = ColumnComparisonCheck({"table": "test_col_comparison_fail", "schema": "test", "expression": "x != y", "config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 1)
        self.assertTrue(u.failed)
        self.assertEqual(u.failed_rows.iloc[0].x, 1)
        self.assertEqual(u.failed_rows.iloc[0].y, 1)


    @data("impala", "postgres")
    def test_col_comparison_success(self, type):
        u = ColumnComparisonCheck({"table": "test_col_comparison_success", "schema": "test", "expression": "x != y", "config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

if __name__ == '__main__':
    unittest.main()
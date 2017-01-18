from tests.base_test import BaseTest

from checks.null_check import NullCheck

from ddt import ddt, data

@ddt
class TestNullCheck(BaseTest):

    @classmethod
    def sql(cls, type):
        if type == "impala":
            return """
                    CREATE TABLE test.test_null_fail (                            
                       id INT,                                                     
                       status STRING                                               
                     );
                    insert into test.test_null_fail(id, status) values (1, NULL);
                    CREATE TABLE test.test_null_success (                            
                       id INT,                                                        
                       status STRING                                                  
                     );
                    insert into test.test_null_success(id, status) values (1, 'okay');
                """
        else:
            return """
                CREATE TABLE test.test_null_fail (                            
                   id INT,                                                     
                   status VARCHAR(50)                                               
                 );
                insert into test.test_null_fail(id, status) values (1, NULL);
                CREATE TABLE test.test_null_success (                            
                   id INT,                                                        
                   status VARCHAR(50)                                                  
                 );
                insert into test.test_null_success(id, status) values (1, 'okay');
            """

    @data("impala", "postgres")
    def test_null_failure(self, type):
        u = NullCheck({"table": "test_null_fail", "schema": "test", "column": "status", "config": self.__class__.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 1)
        self.assertTrue(u.failed)
        self.assertEqual(u.failed_rows.iloc[0].id, 1)

    @data("impala", "postgres")
    def test_null_success(self, type):
        u = NullCheck({"table": "test_null_success", "schema": "test", "column": "status", "config": self.__class__.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

if __name__ == '__main__':
    unittest.main()
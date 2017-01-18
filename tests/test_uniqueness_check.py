from tests.base_test import BaseTest

from checks.uniqueness_check import UniquenessCheck

from ddt import ddt, data

@ddt
class TestUniquenessCheck(BaseTest):

    @classmethod
    def sql(cls, type):
        return """

             CREATE TABLE test.test_uniqueness_fail (                            
               id INT                                                            
             );


            insert into test.test_uniqueness_fail(id) values
              (1), (2), (1);

            CREATE TABLE test.test_uniqueness_success (                            
               id INT                                                               
             );

            insert into test.test_uniqueness_success(id) values
              (1), (2);

            """
    

    @data("impala", "postgres")
    def test_uniqueness_failure(self, type):
        u = UniquenessCheck({"table": "test_uniqueness_fail", "schema": "test", "column": "id", "config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 1)
        self.assertTrue(u.failed)
        self.assertEqual(u.failed_rows.iloc[0].id, 1)


    @data("impala", "postgres")
    def test_uniqueness_success(self, type):
        u = UniquenessCheck({"table": "test_uniqueness_success", "schema": "test", "column": "id", "config": self.config(type)})
        u.run()

        self.assertEqual(len(u.failed_rows), 0)
        self.assertFalse(u.failed)

if __name__ == '__main__':
    unittest.main()
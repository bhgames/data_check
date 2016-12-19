from tests.base_test import BaseTest

from checks.id_gap_check import IdGapCheck

import pandas as pd
import io
import requests
import os

class TestS3(BaseTest):

    def test_s3_store_on_failure(self):
        u = IdGapCheck({"table": "test_id_gap", "schema": "test", "column": "id", "threshold": "3", "config": self.config()})
        u.run()

        uri = u.failed_row_s3_uri

        s = requests.get(uri).content
        c = pd.read_csv(io.StringIO(s.decode('utf-8')))

        self.assertTrue(u.failed_rows.equals(c))

    def test_s3_nonstore_on_success(self):
        u = IdGapCheck({"table": "test_id_gap", "schema": "test", "column": "id", "threshold": "30", "config": self.config()})
        u.run()
        self.assertFalse(hasattr(u, 'failed_row_s3_uri'))


    def test_explode_if_aws_yaml_not_present(self):
        if not os.path.isfile('config/aws.yml'):
            self.assertFalse(True, "Please copy config/aws.yml.sample to config/aws.yml and enter credentials to test this functionality.")

if __name__ == '__main__':
    unittest.main()
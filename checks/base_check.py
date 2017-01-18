from connections.impala_connection import ImpalaConnection
from connections.postgres_connection import PostgresConnection
import pandas as pd
from impala.util import as_pandas
import pandas as pd
from StringIO import StringIO
import os
import boto3
from uuid import uuid4
import yaml
import traceback

class BaseCheck(object):
    def __init__(self, opts = {}):
        self.table = opts["table"]
        self.schema = opts["schema"]
        self.config = opts["config"]

        if self.config['data_source_type'] not in self.__class__.valid_connections():
            raise ValueError("Unsupported DataSource for Check: {}".format(self.config['data_source_type']))

        self.log_metadata = opts["log_metadata"] if "log_metadata" in opts else {}
        self.log = opts["log"] if "log" in opts else None
        self.failed = False

        column = opts["column"] if "column" in opts else None
        expression = opts["expression"] if "expression" in opts else None
        threshold = opts["threshold"] if "threshold" in opts else None
        self.query_settings = { 'table': self.table, 'col': column, 'threshold': threshold, 'schema': self.schema, 'expression': expression }


    def add_log(self, event, message, extra_meta = {}):
        if self.log:
            extra_meta.update(self.log_metadata)
            self.log.add_log(event, message, extra_meta)


    def add_results_csv_to_s3(self):
        if self.failed:
            if(os.path.isfile('config/aws.yml')):
                with open('config/aws.yml', 'r') as f:
                    config = yaml.load(f)

                csv_buffer = StringIO()
                self.failed_rows.to_csv(csv_buffer)
                s3_resource = boto3.resource('s3', aws_access_key_id=config['access_key_id'], aws_secret_access_key=config['secret_access_key'])

                name =  config['prefix'] + "%s_%s_%s_%s.csv" % (self.schema, self.table, self.__class__.__name__, uuid4())
                try:
                    s3_resource.Object(config['bucket_name'], name).put(Body=csv_buffer.getvalue())
                   
                    # generate 5 year key
                    s3_client = boto3.client('s3', aws_access_key_id=config['access_key_id'], aws_secret_access_key=config['secret_access_key'])
                    self.failed_row_s3_uri = s3_client.generate_presigned_url('get_object', Params = {'Bucket': config['bucket_name'], 'Key': name}, ExpiresIn = 3600*24*365*5)

                    self.add_log("collection_storage", "Failed rows stored at %s" % (self.failed_row_s3_uri))
                except:
 		            self.add_log("collection_storage_failed", 
                        "Failed to record saved rows", 
                        { "traceback": traceback.format_exc() })
            else:
                self.add_log("warning", "Not collecting failed rows because you do not have a config/aws.yml set.")


    def run(self):
        connection = eval(self.config["data_source_type"].title() + "Connection")

        with connection(**self.config) as db:
            self.inner_run(db)
            if self.failed:
                self.add_log("check_failed", "Check fails")
            else:
                self.add_log("check_succeeded", "Check succeeds")
            self.run_failed_rows_query(db)
            self.add_results_csv_to_s3()


    def inner_run(self, db):
        cur = db.cursor()

        query = self.collection_query(self.config['data_source_type']);

        self.add_log("collection", "Run query %s" % (query))

        cur.execute(query)

        row = cur.fetchone()

        self.add_log("result", "Query came back with count %s" %(row[0]))

        self.failed = row[0] > 0


    def collection_query(self, type):
        raise ValueError("Implement a collection_query method for your check!")


    def failed_rows_query(self, type):
        return None


    def run_failed_rows_query(self, db):
        cur = db.cursor()

        frq = self.failed_rows_query(self.config['data_source_type'])
        if self.failed and os.path.isfile('config/aws.yml') and frq:
            self.add_log("collection", "Collect failed rows with query %s" % frq)

            cur.execute(frq)

            self.failed_rows = as_pandas(cur)

            self.add_log("result", "Failed Row Result Count: %s" % (len(self.failed_rows)))
        else:
            self.failed_rows = pd.DataFrame()

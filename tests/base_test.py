import unittest

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from os import environ
import traceback
from connections.impala_connection import ImpalaConnection
from connections.postgres_connection import PostgresConnection

environ['DCHK_ENV'] = 'test'

import models.helpers.base
engine = models.helpers.base.get_new_engine()

models.helpers.base.init(engine) # Initialize base declarative class.

from models import *
from models.data_source import DataSource, DataSourceType
db_session = models.helpers.base.db_session

class BaseTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        models.helpers.base.Base.metadata.create_all(engine)
        from celery_jobs.job_runs import app as celery_app
        celery_app.conf.update(CELERY_ALWAYS_EAGER=True)

        for type in ["postgres", "impala"]:
            config = BaseTest.config(type)
            connection = eval(type.title() + "Connection")
            schema = "database" if type == "impala" else "schema"
            
            with connection(**config) as db:
                c = db.cursor()
                c.execute("drop {} if exists test cascade".format(schema))
                c.execute("create {} test".format(schema))

                for stmt in cls.sql(type).split(";"):
                    if stmt.strip() == "":
                        continue
                    try:
                        c.execute(stmt)
                    except Exception:
                        print "Stmt " + stmt + " failed:"
                        traceback.print_exc()
                        raise

                db.commit()
    
    def setUp(self):
        models.helpers.base.Base.metadata.create_all(engine)
        self.s = db_session


    def tearDown(self):
        self.s.remove()
        models.helpers.base.Base.metadata.drop_all(engine)


    def dummy_datasource(self):
        config = self.__class__.config("impala")
        config["data_source_type"] = getattr(DataSourceType, config["data_source_type"])
        config["schemas"] = ["test"]

        d = DataSource(**config)
        return d

    @classmethod
    def config(cls, type):
        if type == "impala":
            return {
                "host": "localhost",
                "port": 21050,
                "user": None,
                "password": None,
                "dbname": None,
                "data_source_type": DataSourceType.impala.value
            }
        else:
            return {
                "host": "localhost",
                "port": 5432,
                "user": None,
                "password": None,
                "dbname": "test",
                "data_source_type": DataSourceType.postgres.value
            }
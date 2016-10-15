import unittest

from sqlalchemy import create_engine
from sqlalchemy import MetaData
import models.helpers.base

models.helpers.base.init() # Initialize base declarative class.

from models import *

engine = create_engine('postgresql://localhost:5432/data_check_test')
metadata = MetaData()

class BaseTest(unittest.TestCase):

    def setUp(self):
        models.helpers.base.Base.metadata.create_all(engine)


    def tearDown(self):
        models.helpers.base.Base.metadata.drop_all(engine)

    def config(self):
        return {
            "host": "localhost",
            "port": 21050
        }
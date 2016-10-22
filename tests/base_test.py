import unittest

from sqlalchemy import create_engine
from sqlalchemy import MetaData
import models.helpers.base
engine = create_engine('postgresql://localhost:5432/data_check_test')

models.helpers.base.init(engine) # Initialize base declarative class.

from models import *

Session = models.helpers.base.Session

class BaseTest(unittest.TestCase):

    def setUp(self):
        models.helpers.base.Base.metadata.create_all(engine)
        self.s = Session()


    def tearDown(self):
        self.s.close()
        models.helpers.base.Base.metadata.drop_all(engine)


    def config(self):
        return {
            "host": "localhost",
            "port": 21050,
            "user": None,
            "password": None
        }
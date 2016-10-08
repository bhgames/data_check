import unittest

from checks.date_gap_check import DateGapCheck

class BaseTest(unittest.TestCase):

    def config(self):
        return {
            "host": "localhost",
            "port": 21050
        }
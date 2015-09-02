import json
import os
import unittest
from protocols.GelProtocols import *

__author__ = 'antonior'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class TestRDParticipantAndPedigree(unittest.TestCase):
    def test_validation(self):
        fd = file(os.path.join(BASE_DIR, "resources", "TestingData", "InterpretedGenomeRDExample.json"))
        dict = json.load(fd)
        self.assertTrue(InterpretationAnalysis.validate(dict))






if __name__ == '__main__':
    unittest.main()
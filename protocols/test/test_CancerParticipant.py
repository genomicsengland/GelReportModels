import json
import os
import unittest
from protocols.GelProtocols import *

__author__ = 'antonior'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class TestCancerParticipant(unittest.TestCase):
    def test_validation_participant(self):
        fd = file(os.path.join(BASE_DIR, "resources", "TestingData", "CancerParticipantExample2.json"))
        dict = json.load(fd)
        cancerParticipant = CancerParticipant.fromJsonDict(dict)
        self.assertTrue(CancerParticipant.validate(cancerParticipant.toJsonDict()))

    def test_validation_demographics(self):
        fd = file(os.path.join(BASE_DIR, "resources", "TestingData", "CancerParticipantExample2.json"))
        dict = json.load(fd)
        cancerParticipant = CancerParticipant.fromJsonDict(dict)
        demogrphics = cancerParticipant.cancerDemographics

        self.assertTrue(CancerDemographics.validate(demogrphics.toJsonDict()))

    def test_validation_cancerSamples(self):
        fd = file(os.path.join(BASE_DIR, "resources", "TestingData", "CancerParticipantExample2.json"))
        dict = json.load(fd)
        cancerParticipant = CancerParticipant.fromJsonDict(dict)
        samples = cancerParticipant.cancerSamples
        self.assertTrue(CancerSample.validate(samples[0].toJsonDict()))

    def test_validation_matchedSamples(self):
        fd = file(os.path.join(BASE_DIR, "resources", "TestingData", "CancerParticipantExample2.json"))
        dict = json.load(fd)
        cancerParticipant = CancerParticipant.fromJsonDict(dict)
        matches = cancerParticipant.matchedSamples
        self.assertTrue(MatchedSamples.validate(matches[0].toJsonDict()))


if __name__ == '__main__':
    unittest.main()
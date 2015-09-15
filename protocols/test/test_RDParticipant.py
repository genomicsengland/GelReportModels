import json
import os
import unittest
from protocols.GelProtocols import *

__author__ = 'antonior'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class TestRDParticipantAndPedigree(unittest.TestCase):
    def test_validation_pedigree(self):
        fd = file(os.path.join(BASE_DIR, "resources", "TestingData", "RDParticipantExample.json"))
        dict = json.load(fd)
        pedigree = Pedigree.fromJsonDict(dict)
        self.assertTrue(Pedigree.validate(pedigree.toJsonDict()))

    def test_validation_participant(self):
        fd = file(os.path.join(BASE_DIR, "resources", "TestingData", "RDParticipantExample.json"))
        dict = json.load(fd)
        pedigree = Pedigree.fromJsonDict(dict)
        self.assertTrue(RDParticipant.validate(pedigree.participants[0].toJsonDict()))

    def test_validation_disease(self):
        fd = file(os.path.join(BASE_DIR, "resources", "TestingData", "RDParticipantExample.json"))
        dict = json.load(fd)
        pedigree = Pedigree.fromJsonDict(dict)
        self.assertTrue(Disorder.validate(pedigree.participants[0].disorderList[0].toJsonDict()))

    def test_validation_consentStatus(self):
        fd = file(os.path.join(BASE_DIR, "resources", "TestingData", "RDParticipantExample.json"))
        dict = json.load(fd)
        pedigree = Pedigree.fromJsonDict(dict)
        self.assertTrue(ConsentStatus.validate(pedigree.participants[0].consentStatus.toJsonDict()))

    def test_validation_hpoTerm(self):
        fd = file(os.path.join(BASE_DIR, "resources", "TestingData", "RDParticipantExample.json"))
        dict = json.load(fd)
        pedigree = Pedigree.fromJsonDict(dict)
        self.assertTrue(HpoTerm.validate(pedigree.participants[0].hpoTermList[0].toJsonDict()))



if __name__ == '__main__':
    unittest.main()
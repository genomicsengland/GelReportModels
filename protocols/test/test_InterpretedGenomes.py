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

    def test_reported_variant(self):
        fd = file(os.path.join(BASE_DIR, "resources", "TestingData", "InterpretedGenomeRDExample.json"))
        dict = json.load(fd)
        analysis = InterpretationAnalysis.fromJsonDict(dict)
        variants = analysis.reportedVariants
        for v in variants:
            self.assertTrue(ReportedVariant.validate(v.toJsonDict()))

    def test_report_events(self):
        fd = file(os.path.join(BASE_DIR, "resources", "TestingData", "InterpretedGenomeRDExample.json"))
        dict = json.load(fd)
        analysis = InterpretationAnalysis.fromJsonDict(dict)
        variants = analysis.reportedVariants
        for v in variants:
            events = v.reportEvents
            for event in events:
                self.assertTrue(ReportEvent.validate(event.toJsonDict()))

    def test_genes(self):
        fd = file(os.path.join(BASE_DIR, "resources", "TestingData", "InterpretedGenomeRDExample.json"))
        dict = json.load(fd)
        analysis = InterpretationAnalysis.fromJsonDict(dict)
        variants = analysis.reportedVariants
        for v in variants:
            events = v.reportEvents
            for event in events:
                self.assertTrue(ReportEvent.validate(event.toJsonDict()))

    def test_called_genotype(self):
        fd = file(os.path.join(BASE_DIR, "resources", "TestingData", "InterpretedGenomeRDExample.json"))
        dict = json.load(fd)
        analysis = InterpretationAnalysis.fromJsonDict(dict)
        variants = analysis.reportedVariants
        for v in variants:
            genotypes = v.calledGenotypes
            for genotype in genotypes:
                self.assertTrue(CalledGenotype.validate(genotype.toJsonDict()))



if __name__ == '__main__':
    unittest.main()
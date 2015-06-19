import json
import os
import unittest
from GelReportModels.protocols.GelProtcols import RDParticipant, ConsentStatus

__author__ = 'antonior'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class TestRDParticipant(unittest.TestCase):

    def create_participant(self):
        new_rd_participant = RDParticipant()
        new_rd_participant.FamilyId = 100
        new_rd_participant.id = 1
        new_rd_participant.father = 6
        new_rd_participant.mother = 5
        new_rd_participant.dataModelVersion = "0.0"
        new_rd_participant.sex = "male"
        new_rd_participant.consentStatus = ConsentStatus()
        new_rd_participant.consentStatus.secondaryFindingConsent = "NO"
        new_rd_participant.consentStatus.carrierStatusConsent = "YES"
        return new_rd_participant

    def test_preprop(self):
        os.system("java -jar " + os.path.join(BASE_DIR, "resources", "avro-tools-1.7.7.jar") + " idl2schemata " +
                  os.path.join(BASE_DIR, "schemas", "IDLs", "InterpretationRequestRD.avdl") + " "
                  + os.path.join(BASE_DIR, "schemas", "JSONs", "ReportTriggeringRD"))

        os.system("java -jar " + os.path.join(BASE_DIR, "resources", "avro-tools-1.7.7.jar") + " idl2schemata " +
                  os.path.join(BASE_DIR, "schemas", "IDLs", "CancerParticipant.avdl") + " "
                  + os.path.join(BASE_DIR, "schemas", "JSONs", "ReportTriggeringRD"))

        new_rd_participant = self.create_participant()
        self.assertTrue(isinstance(new_rd_participant, RDParticipant))

    def test_write(self):
        fdw = file(os.path.join(BASE_DIR, "resources", "RDParticipant.json"), "w")
        fdw.write(self.create_participant().toJsonString())
        fdw.close()

    def test_validation(self):
        fd = file(os.path.join(BASE_DIR, "resources", "RDParticipant.json"))
        dict = json.loads(fd.readline())
        self.assertTrue(RDParticipant.validate(dict))

    def test_read(self):
        new_rd_participant = self.create_participant()
        fd = file(os.path.join(BASE_DIR, "resources", "RDParticipant.json"))
        dict = json.loads(fd.readline())
        generate_rd_participant = RDParticipant.fromJsonDict(dict)
        self.assertEqual(new_rd_participant.toJsonDict(), generate_rd_participant.toJsonDict())



if __name__ == '__main__':
    unittest.main()
import os
from unittest import TestCase
from GelReportModels.protocols.GelProtcols import RDParticipant, ConsentStatus, HpoTerm, Disorder, Pedigree
import random
__author__ = 'antonior'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
class TestReport(TestCase):

    def crate_random_hpoterm_array(self, length):
        hpoterm_array = []
        for i in range(0, length):
            fd = file(os.path.join(BASE_DIR, "resources", "hpo_sample.txt"))
            hpoterm = fd.readlines(random.choice(range(0, 99)))[0].split("\t")[4]
            age = random.choice(range(0, 70))
            hpoterm_array.append(hpoterm)
        return hpoterm_array

    def create_participant(self, familyID, id, father, mother, sex):
        new_rd_participant = RDParticipant()
        new_rd_participant.id = id
        new_rd_participant.FamilyId = familyID
        new_rd_participant.father = father
        new_rd_participant.mother = mother
        new_rd_participant.dataModelVersion = "0.0"
        new_rd_participant.sex = sex
        new_rd_participant.consentStatus = ConsentStatus()
        new_rd_participant.hpoTerms = self.crate_random_hpoterm_array(random.choice(range(0, 4)))
        new_rd_participant.disorders = []

        new_rd_participant.consentStatus.secondaryFindingConsent = "YES"
        new_rd_participant.consentStatus.carrierStatusConsent = "YES"
        return new_rd_participant

    def test_create_random_pedigree(self):

        sex = random.choice(("male", "female", "unknown"))
        moi = random.choice(("MONOALLELIC, AUTOSOMAL OR PSEUDOAUTOSOMAL, NOT IMPRINTED", "BIALLELIC, AUTOSOMAL OR PSEUDOAUTOSOMAL"))
        proband = self.create_participant(10, 1, 2, 3, sex)
        father = self.create_participant(10, 2, None, None, "male")
        mother = self.create_participant(10, 3, None, None, "female")

        if moi == "MONOALLELIC, AUTOSOMAL OR PSEUDOAUTOSOMAL, NOT IMPRINTED":
            father.disorders.append("268000")
            proband.disorders.append("268000")
            mother.disorders = None
        if moi == "BIALLELIC, AUTOSOMAL OR PSEUDOAUTOSOMAL":
            proband.disorders.append("268000")
            mother.disorders = None
            father.disorders = None

        pedigree = Pedigree()
        pedigree.familyId = 10
        pedigree.participants = [proband, father, mother]

        fdw = file(os.path.join(BASE_DIR, "resources", "RDPedigree.json"), "w")
        fdw.write(pedigree.toJsonString())
        fdw.close()

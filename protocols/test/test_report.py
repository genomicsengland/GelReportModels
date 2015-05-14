import os
from unittest import TestCase
from GelReportModels.protocols.GelProtcols import RDParticipant, ConsentStatus, HpoTerm, Disorder
import random
__author__ = 'antonior'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
class TestReport(TestCase):


    def crate_random_hpoterm_array(self, length):
        hpoterm_array = []
        for i in range(0, length):
            fd = file(os.path.join(BASE_DIR, "resources", "hpo_sample.txt"))
            hpoterm = fd.readlines(random.choice(range(0, 99)))[0].split("\t")[3]
            age = random.choice(range(0, 70))
            new_hpo = HpoTerm()
            new_hpo.term = hpoterm
            new_hpo.ageOfOnset = age
            hpoterm_array.append(new_hpo)
        return hpoterm_array




    def create_participant(self, id, father, mother, sex):
        new_rd_participant = RDParticipant()
        new_rd_participant.id = id
        new_rd_participant.father = father
        new_rd_participant.mother = mother
        new_rd_participant.dataModelVersion = "0.0"
        new_rd_participant.sex = sex
        new_rd_participant.consentStatus = ConsentStatus()
        new_rd_participant.hpoTerms = self.crate_random_hpoterm_array(random.choice(range(0, 4)))
        new_rd_participant.disorders = Disorder()

        new_rd_participant.consentStatus.secondaryFindingConsent = "YES"
        new_rd_participant.consentStatus.carrierStatusConsent = "YES"
        return new_rd_participant


    def create_random_pedigree(self):

        sex = random.choice(("male", "female", "unknown"))
        moi = random.choice(("MONOALLELIC, AUTOSOMAL OR PSEUDOAUTOSOMAL, NOT IMPRINTED", "BIALLELIC, AUTOSOMAL OR PSEUDOAUTOSOMAL"))

        

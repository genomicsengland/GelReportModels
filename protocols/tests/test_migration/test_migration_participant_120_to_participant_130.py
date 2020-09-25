from protocols import participant_1_2_0, participant_1_3_0
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_participant_120_to_participant_130 import MigrateParticipant120To130


class TestMigrateParticipant120To131(TestCaseMigration):
    old_model = participant_1_2_0
    new_model = participant_1_3_0

    def test_migrate_pedigree(self):
        pedigree_1_2_0 = self.get_valid_object(object_type=self.old_model.Pedigree, version=self.version_7_3,
                                               fill_nullables=True
                                               )
        pedigree_1_3_0 = MigrateParticipant120To130().migrate_pedigree(old_pedigree=pedigree_1_2_0)
        self.assertIsInstance(pedigree_1_3_0, self.new_model.Pedigree)
        self.assertTrue(self.new_model.Pedigree.validate(pedigree_1_3_0.toJsonDict()))
        self.assertIsInstance(pedigree_1_3_0.members[0].samples[0].labSampleId, str)

    def test_migrate_cancer_participant(self):
        cancer_participant_1_2_0 = self.get_valid_object(object_type=self.old_model.CancerParticipant,
                                                         version=self.version_7_3,
                                                         fill_nullables=True
                                                         )
        cancer_participant_1_3_0 = MigrateParticipant120To130().migrate_cancer_participant(
            old_cancer_participant=cancer_participant_1_2_0)
        self.assertIsInstance(cancer_participant_1_3_0, self.new_model.CancerParticipant)
        self.assertTrue(self.new_model.CancerParticipant.validate(cancer_participant_1_3_0.toJsonDict()))
        self.assertIsInstance(cancer_participant_1_3_0.tumourSamples[0].labSampleId, str)
        self.assertIsInstance(cancer_participant_1_3_0.germlineSamples[0].labSampleId, str)

    def test_migrate_referral(self):
        referral_1_2_0 = self.get_valid_object(object_type=self.old_model.Referral,
                                               version=self.version_7_3,
                                               fill_nullables=True
                                               )
        referral_1_3_0 = MigrateParticipant120To130().migrate_referral(
            old_referral=referral_1_2_0)
        self.assertIsInstance(referral_1_3_0, self.new_model.Referral)
        self.assertTrue(self.new_model.Referral.validate(referral_1_3_0.toJsonDict()))
        self.assertIsInstance(referral_1_3_0.referralTests[0].tumourSamples[0].labSampleId, str)
        self.assertIsInstance(referral_1_3_0.referralTests[0].germlineSamples[0].labSampleId, str)
        self.assertIsInstance(referral_1_3_0.pedigree.members[0].samples[0].labSampleId, str)
        self.assertIsInstance(referral_1_3_0.cancerParticipant.tumourSamples[0].labSampleId, str)
        self.assertIsInstance(referral_1_3_0.cancerParticipant.germlineSamples[0].labSampleId, str)

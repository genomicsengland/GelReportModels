from protocols import participant_1_1_2, participant_1_1_3
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_participant_112_to_participant_113 import MigrateParticipant112To113


class TestMigrateParticipant120To131(TestCaseMigration):
    old_model = participant_1_1_2
    new_model = participant_1_1_3

    def test_migrate_pedigree(self):
        pedigree_1_1_2 = self.get_valid_object(object_type=self.old_model.Pedigree, version=self.version_7_2,
                                               fill_nullables=True
                                               )
        pedigree_1_1_3 = MigrateParticipant112To113().migrate_pedigree(old_pedigree=pedigree_1_1_2)
        self.assertIsInstance(pedigree_1_1_3, self.new_model.Pedigree)
        self.assertTrue(self.new_model.Pedigree.validate(pedigree_1_1_3.toJsonDict()))
        self.assertIsInstance(pedigree_1_1_3.members[0].samples[0].labSampleId, str)

    def test_migrate_cancer_participant(self):
        cancer_participant_1_1_2 = self.get_valid_object(object_type=self.old_model.CancerParticipant,
                                                         version=self.version_7_2,
                                                         fill_nullables=True
                                                         )
        cancer_participant_1_1_3 = MigrateParticipant112To113().migrate_cancer_participant(
            old_cancer_participant=cancer_participant_1_1_2)
        self.assertIsInstance(cancer_participant_1_1_3, self.new_model.CancerParticipant)
        self.assertTrue(self.new_model.CancerParticipant.validate(cancer_participant_1_1_3.toJsonDict()))
        self.assertIsInstance(cancer_participant_1_1_3.tumourSamples[0].labSampleId, str)
        self.assertIsInstance(cancer_participant_1_1_3.germlineSamples[0].labSampleId, str)
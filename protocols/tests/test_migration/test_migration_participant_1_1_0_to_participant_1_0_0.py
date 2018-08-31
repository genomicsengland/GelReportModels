import factory.fuzzy
from random import randint

from protocols import participant_1_0_0
from protocols import participant_1_1_0
from protocols.util.dependency_manager import VERSION_61
from protocols.util.dependency_manager import VERSION_500
from protocols.util.dependency_manager import VERSION_400
from protocols.util.factories.avro_factory import FactoryAvro
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_participant_110_to_participant_100 import MigrateParticipant110To100


class TestMigrateParticipant110To100(TestCaseMigration):

    old_model = participant_1_1_0
    new_model = participant_1_0_0

    def test_migrate_pedigree(self):
        pedigree_1_1_0 = self.get_valid_object(object_type=self.old_model.Pedigree, version=self.version_7_0)
        pedigree_1_0_0 = MigrateParticipant110To100().migrate_pedigree(old_pedigree=pedigree_1_1_0)
        self.assertIsInstance(pedigree_1_0_0, self.new_model.Pedigree)
        self.assertTrue(pedigree_1_0_0.validate(pedigree_1_0_0.toJsonDict()))

    def test_migrate_pedigree_member(self):
        pm_1_1_0 = self.get_valid_object(object_type=self.old_model.PedigreeMember, version=self.version_7_0)
        pm_1_0_0 = MigrateParticipant110To100()._migrate_pedigree_member(old_member=pm_1_1_0)
        self.assertIsInstance(pm_1_0_0, self.new_model.PedigreeMember)
        self.assertTrue(pm_1_0_0.validate(pm_1_0_0.toJsonDict()))

        for attribute in [
            "pedigreeId", "isProband", "participantId", "gelSuperFamilyId", "yearOfBirth", "fatherId", "motherId",
            "superFatherId", "superMotherId", "twinGroup"
        ]:
            self.assertEqual(getattr(pm_1_1_0, attribute), getattr(pm_1_0_0, attribute))

    def test_migrate_cancer_participant(self):
        p_1_1_0 = self.get_valid_object(
            object_type=self.old_model.CancerParticipant, version=self.version_7_0, fill_nullables=False)
        p_1_0_0 = MigrateParticipant110To100().migrate_cancer_participant(old_instance=p_1_1_0)
        self.assertIsInstance(p_1_0_0, self.new_model.CancerParticipant)
        self.assertTrue(p_1_0_0.validate(p_1_0_0.toJsonDict()))



import factory.fuzzy
from random import randint

from protocols import participant_1_0_3
from protocols import participant_1_1_0
from protocols.util.dependency_manager import VERSION_61
from protocols.util.dependency_manager import VERSION_500
from protocols.util.dependency_manager import VERSION_400
from protocols.util.factories.avro_factory import FactoryAvro
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_participant_1_1_0_to_participant_1_0_3 import MigrateParticipant110To103


class TestMigrateParticipant110To100(TestCaseMigration):

    old_model = participant_1_1_0
    new_model = participant_1_0_3

    def test_migrate_cancer_participant(self):
        p_1_1_0 = self.get_valid_object(object_type=self.old_model.CancerParticipant, version=self.version_6_1)
        p_1_0_3 = MigrateParticipant110To103().migrate_cancer_participant(old_participant=p_1_1_0)
        self.assertIsInstance(p_1_0_3, self.new_model.CancerParticipant)
        self.assertTrue(p_1_0_3.validate(p_1_0_3.toJsonDict()))

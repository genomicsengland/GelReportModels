from unittest import TestCase

from protocols import reports_4_0_0
from protocols import reports_4_2_0_SNAPSHOT
from protocols import participant_1_0_4_SNAPSHOT
from protocols import participant_1_0_0
from protocols.migration import MigrateReports420SNAPSHOTTo400
from protocols.migration import MigrationParticipants104SNAPSHOTTo100
from protocols.util.generate_mock_objects import get_valid_cancer_interpretation_request_4_2_0_SNAPSHOT


class TestMigrateReports420To4(TestCase):

    old_model = reports_4_2_0_SNAPSHOT
    new_model = reports_4_0_0

    def test_migrate_cir_420_to_400(self):

        cir_420 = get_valid_cancer_interpretation_request_4_2_0_SNAPSHOT()

        # Check cir_420 is a valid reports_4_2_0_SNAPSHOT CancerInterpretationRequest object
        self.assertIsInstance(cir_420, self.old_model.CancerInterpretationRequest)
        self.assertTrue(cir_420.validate(jsonDict=cir_420.toJsonDict()))

        migrated_object = MigrateReports420SNAPSHOTTo400().migrate_cancer_interpretation_request(
            cancer_interpretation_request=cir_420
        )

        # Check migrated_object is a valid reports_4_0_0 CancerInterpretationRequest object
        self.assertIsInstance(migrated_object, self.new_model.CancerInterpretationRequest)
        self.assertTrue(migrated_object.validate(jsonDict=migrated_object.toJsonDict()))

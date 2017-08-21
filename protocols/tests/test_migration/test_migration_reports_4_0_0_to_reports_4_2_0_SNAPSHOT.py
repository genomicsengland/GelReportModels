from unittest import TestCase

from protocols import reports_4_0_0
from protocols import reports_4_2_0_SNAPSHOT
from protocols.migration import MigrateReports400To420SNAPSHOT
from protocols.util import get_valid_cancer_interpretation_request_4_0_0


class TestMigrateReports420To4(TestCase):

    old_model = reports_4_0_0
    new_model = reports_4_2_0_SNAPSHOT

    def test_migrate_cir_400_to_420(self):

        cir_400 = get_valid_cancer_interpretation_request_4_0_0()

        cir_400.cancerParticipant.LDPCode = 'test_LDP_code_migrate_cir_400_to_420'

        self.assertIsInstance(cir_400, self.old_model.CancerInterpretationRequest)
        self.assertTrue(cir_400.validate(cir_400.toJsonDict()))

        migrated_cir = MigrateReports400To420SNAPSHOT().migrate_cancer_interpretation_request(
            cancer_interpretation_request=cir_400
        )
        self.assertIsInstance(migrated_cir, self.new_model.CancerInterpretationRequest)
        self.assertTrue(migrated_cir.validate(migrated_cir.toJsonDict()))

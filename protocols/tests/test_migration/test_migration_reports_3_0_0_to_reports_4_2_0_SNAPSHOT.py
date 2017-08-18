from unittest import TestCase

from protocols.migration import MigrateReports3To420SNAPSHOT
from protocols.reports_4_2_0_SNAPSHOT import InterpretationRequestRD as InterpretationRequestRD_new
from protocols.reports_3_0_0 import InterpretationRequestRD as InterpretationRequestRD_old
from protocols.util import get_valid_interpretation_request_rd_3_0_0


class TestMigrateReports3To420SNAPSHOT(TestCase):

    def test_migrate_interpretation_request(self):

        old_interpretation_request_rd = get_valid_interpretation_request_rd_3_0_0()

        # Check old_interpretation_request_rd is a valid reports_3_0_0 ReportedSomaticVariants object
        self.assertTrue(isinstance(old_interpretation_request_rd, InterpretationRequestRD_old))
        self.assertTrue(old_interpretation_request_rd.validate(jsonDict=old_interpretation_request_rd.toJsonDict()))

        migrated_object = MigrateReports3To420SNAPSHOT().migrate_interpretation_request_rd(
            old_interpretation_request_rd=old_interpretation_request_rd
        )

        # Check migrated_object is a valid reports_4_2_0_SNAPSHOT InterpretationRequestRD object
        self.assertTrue(isinstance(migrated_object, InterpretationRequestRD_new))
        self.assertTrue(migrated_object.validate(jsonDict=migrated_object.toJsonDict()))

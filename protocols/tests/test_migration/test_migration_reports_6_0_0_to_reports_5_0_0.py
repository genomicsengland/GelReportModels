from protocols import reports_6_0_0
from protocols import reports_5_0_0
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_6_0_0_to_reports_5_0_0 import MigrateReports600To500


class TestMigrateReports600To500(TestCaseMigration):

    old_model = reports_6_0_0
    new_model = reports_5_0_0

    def test_migrate_interpretation_request_rd(self):
        ir_rd_6 = self.get_valid_object(object_type=self.old_model.InterpretationRequestRD, version=self.version_7_0)
        ir_rd_5 = MigrateReports600To500().migrate_interpretation_request_rd(old_instance=ir_rd_6)
        self.assertIsInstance(ir_rd_5, self.new_model.InterpretationRequestRD)
        self.assertTrue(ir_rd_5.validate(ir_rd_5.toJsonDict()))

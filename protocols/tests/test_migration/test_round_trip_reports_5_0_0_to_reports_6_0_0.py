from protocols import reports_6_0_0
from protocols import reports_5_0_0
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_6_0_0_to_reports_5_0_0 import MigrateReports600To500
from protocols.migration.migration_reports_5_0_0_to_reports_6_0_0 import MigrateReports500To600


class TestRoundTripMigrateReports500To600(TestCaseMigration):
    old_model = reports_5_0_0
    new_model = reports_6_0_0

    def test_migrate_interpretation_request_rd(self):
        self._check_rd(fill_nullables=True)

    def test_migrate_interpretation_request_cancer(self):
        self._check_cancer(fill_nullables=True)

    def test_migrate_interpretation_request_rd_with_nulls(self):
        self._check_rd(fill_nullables=False)

    def test_migrate_interpretation_request_cancer_with_nulls(self):
        self._check_cancer(fill_nullables=False)

    def _check_cancer(self, fill_nullables):
        self._check_round_trip_migration(
            MigrateReports500To600().migrate_interpretation_request_cancer,
            MigrateReports600To500().migrate_interpretation_request_cancer,
            self.old_model.CancerInterpretationRequest,
            self.new_model.CancerInterpretationRequest,
            fill_nullables=fill_nullables
        )

    def _check_rd(self, fill_nullables):
        self._check_round_trip_migration(
            MigrateReports500To600().migrate_interpretation_request_rd,
            MigrateReports600To500().migrate_interpretation_request_rd,
            self.old_model.InterpretationRequestRD,
            self.new_model.InterpretationRequestRD,
            fill_nullables=fill_nullables
        )

    def _check_round_trip_migration(self, forward, backward, original_type, new_type, fill_nullables):
        original = self.get_valid_object(
            object_type=original_type, version=self.version_6_1, fill_nullables=fill_nullables)

        original.versionControl = self.old_model.ReportVersionControl()  # to set the right default

        migrated = forward(old_instance=original)
        self.assertIsInstance(migrated, new_type)
        self.assertTrue(migrated.validate(migrated.toJsonDict()))

        round_tripped = backward(old_instance=migrated)
        self.assertIsInstance(round_tripped, original_type)
        self.assertTrue(round_tripped.validate(migrated.toJsonDict()))
        self.assertEqual(round_tripped.toJsonDict(), original.toJsonDict())

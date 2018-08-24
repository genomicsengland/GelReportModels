from protocols import reports_6_0_0, reports_4_0_0
from protocols import reports_5_0_0
from protocols.migration import MigrateReports400To500, MigrateReports500To400
from protocols.reports_5_0_0 import Assembly
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_6_0_0_to_reports_5_0_0 import MigrateReports600To500
from protocols.migration.migration_reports_5_0_0_to_reports_6_0_0 import MigrateReports500To600
from protocols.util.dependency_manager import VERSION_400
from protocols.util.factories.avro_factory import FactoryAvro, GenericFactoryAvro
import factory.fuzzy


class ActionFactory(FactoryAvro):
    class Meta:
        model = reports_4_0_0.Actions

    _version = VERSION_400

    actionType = factory.fuzzy.FuzzyChoice(['therapy', 'therapeutic', 'prognosis', 'diagnosis'])
    status = factory.fuzzy.FuzzyChoice(['clinical', 'pre-clinical'])
    evidence = ["this", "that"]
    drug = factory.fuzzy.FuzzyText()
    variantActionable = factory.fuzzy.FuzzyChoice([True, False])
    comments = ["this", "that"]
    url = factory.fuzzy.FuzzyText()
    evidenceType = factory.fuzzy.FuzzyText()
    source = factory.fuzzy.FuzzyText()


class BaseTestRoundTrip(TestCaseMigration):
    def _check_round_trip_migration(self, forward, backward, original_type, new_type,
                                    fill_nullables, original_version, expect_equality=True):
        original = self.get_valid_object(
            object_type=original_type, version=original_version, fill_nullables=fill_nullables)

        original.versionControl = self.old_model.ReportVersionControl()  # to set the right default

        migrated = forward(original)
        self.assertIsInstance(migrated, new_type)
        self.assertValid(migrated)

        round_tripped = backward(migrated)
        self.assertIsInstance(round_tripped, original_type)
        self.assertValid(round_tripped)

        if expect_equality:
            self.assertEqual(round_tripped.toJsonDict(), original.toJsonDict())

    def assertValid(self, instance):
        validation = instance.validate(instance.toJsonDict(), verbose=True)
        if not validation.result:
            for message in validation.messages:
                print(message)
            self.assertFalse(True)


class TestRoundTripMigrateReports500To600(BaseTestRoundTrip):
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

    def test_migrate_interpretated_genome_cancer(self):
        self._check_round_trip_migration(
            MigrateReports500To600().migrate_cancer_interpreted_genome,
            MigrateReports600To500().migrate_cancer_interpreted_genome,
            self.old_model.CancerInterpretedGenome,
            self.new_model.InterpretedGenome,
            fill_nullables=True,
            original_version=self.version_6_1,
            expect_equality=False
        )

    def test_migrate_interpretated_genome_cancer_with_nulls(self):
        self._check_round_trip_migration(
            MigrateReports500To600().migrate_cancer_interpreted_genome,
            MigrateReports600To500().migrate_cancer_interpreted_genome,
            self.old_model.CancerInterpretedGenome,
            self.new_model.InterpretedGenome,
            fill_nullables=False,
            original_version=self.version_6_1,
            expect_equality=False
        )

    def test_migrate_reported_variant_cancer(self):
        self._check_round_trip_migration(
            MigrateReports500To600().migrate_variant_cancer,
            MigrateReports600To500().migrate_variant_cancer,
            self.old_model.ReportedVariantCancer,
            self.new_model.SmallVariant,
            fill_nullables=True,
            original_version=self.version_6_1,
            expect_equality=False
        )

    def test_migrate_report_event_cancer_action(self):
        self._check_round_trip_migration(
            self._migrate_action,
            lambda actions: MigrateReports600To500().migrate_actions(actions)[0],
            self.old_model.Action,
            self.new_model.Actions,
            fill_nullables=True,
            original_version=self.version_6_1,
            expect_equality=False
        )

    def _migrate_action(self, action):
        action.evidenceType = 'Trial (with, some, words)'
        return MigrateReports500To600().migrate_actions([action])

    def _check_cancer(self, fill_nullables):
        self._check_round_trip_migration(
            MigrateReports500To600().migrate_interpretation_request_cancer,
            MigrateReports600To500().migrate_interpretation_request_cancer,
            self.old_model.CancerInterpretationRequest,
            self.new_model.CancerInterpretationRequest,
            fill_nullables=fill_nullables,
            original_version=self.version_6_1
        )

    def _check_rd(self, fill_nullables):
        self._check_round_trip_migration(
            MigrateReports500To600().migrate_interpretation_request_rd,
            MigrateReports600To500().migrate_interpretation_request_rd,
            self.old_model.InterpretationRequestRD,
            self.new_model.InterpretationRequestRD,
            fill_nullables=fill_nullables,
            original_version=self.version_6_1
        )


class TestRoundTripMigrateReports400To600(BaseTestRoundTrip):
    old_model = reports_4_0_0
    new_model = reports_6_0_0

    def test_migrate_cancer_interpreted_genome(self):
        self._check_round_trip_migration(
            self._migrate_cancer_interpreted_genome_forwards,
            self._migrate_cancer_interpreted_genome_backwards,
            self.old_model.CancerInterpretedGenome,
            self.new_model.InterpretedGenome,
            fill_nullables=True,
            original_version=self.version_4_0_0,
            expect_equality=False
        )

    def test_migrate_cancer_interpreted_genome_with_nulls(self):
        self._check_round_trip_migration(
            self._migrate_cancer_interpreted_genome_forwards,
            self._migrate_cancer_interpreted_genome_backwards,
            self.old_model.CancerInterpretedGenome,
            self.new_model.InterpretedGenome,
            fill_nullables=False,
            original_version=self.version_4_0_0,
            expect_equality=False
        )

    def _migrate_cancer_interpreted_genome_forwards(self, ig):
        return MigrateReports500To600().migrate_cancer_interpreted_genome(
                MigrateReports400To500().migrate_cancer_interpreted_genome(
                    old_instance=ig,
                    assembly=Assembly.GRCh38,
                    participant_id="pid",
                    sample_id="sid",
                    interpretation_request_version=12345,
                    interpretation_service="testing"
                )
            )

    def _migrate_cancer_interpreted_genome_backwards(self, ig):
        return MigrateReports500To400().migrate_cancer_interpreted_genome(
                MigrateReports600To500().migrate_cancer_interpreted_genome(ig)
            )

    def setUp(self):
        GenericFactoryAvro.register_factory(
            reports_4_0_0.Actions, ActionFactory, VERSION_400, fill_nullables=True)
        GenericFactoryAvro.register_factory(
            reports_4_0_0.Actions, ActionFactory, VERSION_400, fill_nullables=False)

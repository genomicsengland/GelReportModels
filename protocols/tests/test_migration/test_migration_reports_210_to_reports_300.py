from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols import reports_3_0_0
from protocols import reports_2_1_0
from protocols.util.dependency_manager import VERSION_210
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.migration.migration_reports_210_to_reports_300 import Migration21To3
import protocols.reports_3_0_0


class TestMigrateReports3To4(TestCaseMigration):

    old_model = reports_2_1_0
    new_model = reports_3_0_0

    def setUp(self):
        # avoids infinite recursion in mocked data
        # now creates another factory generating values for nullable fields
        file_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_2_1_0.File,
            VERSION_210,
            False,
            False
        )
        GenericFactoryAvro.register_factory(
            protocols.reports_2_1_0.File,
            file_factory,
            VERSION_210,
            True
        )

    def test_migrate_clinical_report_rd(self):
        """Also tested with real data"""
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportRD, VERSION_210, fill_nullables=False
        ).create()  # reports_3_0_0.InterpretationRequestRD
        self._validate(old_instance)
        migrated_instance = Migration21To3().migrate_clinical_report(old_instance)
        self._validate(migrated_instance)

        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportRD, VERSION_210, fill_nullables=True
        ).create()  # reports_3_0_0.InterpretationRequestRD
        self._validate(old_instance)
        migrated_instance = Migration21To3().migrate_clinical_report(old_instance)
        self._validate(migrated_instance)

    def test_migrate_interpreted_genome_rd(self):
        """Also tested with real data"""
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_210, fill_nullables=False
        ).create()  # reports_3_0_0.InterpretationRequestRD
        self._validate(old_instance)
        migrated_instance = Migration21To3().migrate_interpreted_genome(old_instance)
        self._validate(migrated_instance)

        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_210, fill_nullables=True
        ).create()  # reports_3_0_0.InterpretationRequestRD
        self._validate(old_instance)
        migrated_instance = Migration21To3().migrate_interpreted_genome(old_instance)
        self._validate(migrated_instance)

    def test_migrate_interpretation_request_rd(self):
        """Also tested with real data"""
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretationRequestRD, VERSION_210, fill_nullables=False
        ).create()  # reports_3_0_0.InterpretationRequestRD
        self._validate(old_instance)
        migrated_instance = Migration21To3().migrate_interpretation_request(old_instance)
        self._validate(migrated_instance)

        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretationRequestRD, VERSION_210, fill_nullables=True
        ).create()  # reports_3_0_0.InterpretationRequestRD
        self._validate(old_instance)
        migrated_instance = Migration21To3().migrate_interpretation_request(old_instance)
        self._validate(migrated_instance)

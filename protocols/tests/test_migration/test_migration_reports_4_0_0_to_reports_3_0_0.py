import factory.fuzzy
from random import randint

from protocols import reports_4_0_0
from protocols import reports_3_0_0
from protocols.util.dependency_manager import VERSION_61
from protocols.util.dependency_manager import VERSION_500
from protocols.util.dependency_manager import VERSION_400
from protocols.util.factories.avro_factory import FactoryAvro
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration import MigrateReports400To300


class TestMigrateReports5To400(TestCaseMigration):

    old_model = reports_4_0_0
    new_model = reports_3_0_0

    def _check_variant_coordinates(self, old_variants, new_variants):
        for new_variant, old_variant in zip(new_variants, old_variants):
            self.assertEqual(new_variant.reference, old_variant.reference)
            self.assertEqual(new_variant.alternate, old_variant.alternate)
            self.assertEqual(new_variant.position, old_variant.position)
            self.assertEqual(new_variant.chromosome, old_variant.chromosome)

    def test_migrate_rd_clinical_report(self, fill_nullables=True):
        # creates a random clinical report RD for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportRD, VERSION_400, fill_nullables=fill_nullables
        ).create(interpretationRequestVersion='1')  # we need to enforce that it can be cast to int

        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        new_instance = MigrateReports400To300().migrate_clinical_report_rd(old_instance=old_instance)
        self.assertIsInstance(new_instance, self.new_model.ClinicalReportRD)
        self._validate(new_instance)
        if fill_nullables:
            self._check_variant_coordinates(
                old_variants=old_instance.candidateVariants,
                new_variants=new_instance.candidateVariants,
            )

    def test_migrate_rd_clinical_report_fill_nullables_false(self):
        self.test_migrate_rd_clinical_report(fill_nullables=False)

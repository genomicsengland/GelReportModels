import factory.fuzzy
from random import randint

from protocols import reports_3_0_0
from protocols import reports_4_0_0
from protocols import reports_5_0_0
from protocols.migration import MigrationHelpers
from protocols.migration import MigrateReports500To400
from protocols.util.dependency_manager import VERSION_61
from protocols.util.dependency_manager import VERSION_500
from protocols.util.dependency_manager import VERSION_400
from protocols.util.factories.avro_factory import FactoryAvro
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_4_0_0_to_reports_3_0_0 import MigrateReports400To300


class TestMigrateReports5To300(TestCaseMigration):

    old_model = reports_5_0_0
    new_model = reports_3_0_0

    def _check_variant_coordinates(self, old_variants, new_variants):
        for new_variant, old_variant in zip(new_variants, old_variants):
            self.assertEqual(new_variant.reference, old_variant.variantCoordinates.reference)
            self.assertEqual(new_variant.alternate, old_variant.variantCoordinates.alternate)
            self.assertEqual(new_variant.position, old_variant.variantCoordinates.position)
            self.assertEqual(new_variant.chromosome, old_variant.variantCoordinates.chromosome)

    def _check_variant_coordinates_4_3(self, old_variants, new_variants):
        for new_variant, old_variant in zip(new_variants, old_variants):
            self.assertEqual(new_variant.reference, old_variant.reference)
            self.assertEqual(new_variant.alternate, old_variant.alternate)
            self.assertEqual(new_variant.position, old_variant.position)
            self.assertEqual(new_variant.chromosome, old_variant.chromosome)

    def test_migrate_rd_clinical_report(self, fill_nullables=True):
        # creates a random clinical report RD for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportRD, VERSION_61, fill_nullables=fill_nullables
        ).create(interpretationRequestVersion='1')  # we need to enforce that it can be cast to int

        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

            #################################################
            # TODO(Greg): Remove this when IP-1394 is resolved
            valid_tiers = ["TIER1", "TIER2", "TIER3", "NONE"]
            for rv in old_instance.variants:
                for re in rv.reportEvents:
                    if re.tier not in valid_tiers:
                        re.tier = valid_tiers[randint(0, len(valid_tiers)-1)]
            #################################################

            valid_genomic_features = [
                self.old_model.GenomicEntityType.regulatory_region,
                self.old_model.GenomicEntityType.gene,
                self.old_model.GenomicEntityType.transcript,
            ]
            for rv in old_instance.variants:
                for re in rv.reportEvents:
                    entity = re.genomicEntities[0]
                    if entity.type not in valid_genomic_features:
                        entity.type = valid_genomic_features[randint(0, len(valid_genomic_features)-1)]

            valid_genotypes = [
                self.old_model.Zygosity.reference_homozygous,
                self.old_model.Zygosity.heterozygous,
                self.old_model.Zygosity.alternate_homozygous,
                self.old_model.Zygosity.missing,
                self.old_model.Zygosity.half_missing_reference,
                self.old_model.Zygosity.half_missing_alternate,
                self.old_model.Zygosity.alternate_hemizigous,
                self.old_model.Zygosity.reference_hemizigous,
                self.old_model.Zygosity.unk,
            ]
            for rv in old_instance.variants:
                for vc in rv.variantCalls:
                    if vc.zygosity not in valid_genotypes:
                        vc.zygosity = valid_genotypes[randint(0, len(valid_genotypes)-1)]

        new_instance_json = MigrationHelpers().reverse_migrate_v5_RD_clinical_report_to_v3(json_dict=old_instance.toJsonDict())
        new_instance = self.new_model.ClinicalReportRD.fromJsonDict(jsonDict=new_instance_json)

        self._validate(new_instance)
        if fill_nullables:
            self._check_variant_coordinates(
                old_variants=old_instance.variants,
                new_variants=new_instance.candidateVariants,
            )

    def test_migrate_rd_clinical_report_nullables_false(self):
        self.test_migrate_rd_clinical_report(fill_nullables=False)

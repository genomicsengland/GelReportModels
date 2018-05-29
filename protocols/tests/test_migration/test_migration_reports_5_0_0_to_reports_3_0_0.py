import factory.fuzzy
from random import randint

from protocols import reports_3_0_0
from protocols import reports_4_0_0
from protocols import reports_5_0_0
from protocols.migration import MigrateReports500To400
from protocols.migration import MigrateReports400To300
from protocols.util.dependency_manager import VERSION_61
from protocols.util.dependency_manager import VERSION_500
from protocols.util.dependency_manager import VERSION_400
from protocols.util.factories.avro_factory import FactoryAvro
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.tests.test_migration.base_test_migration import TestCaseMigration


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


class TestMigrateReports5To400(TestCaseMigration):

    old_model = reports_5_0_0
    halfway_model = reports_4_0_0
    new_model = reports_3_0_0

    def setUp(self):
        GenericFactoryAvro.register_factory(
            reports_4_0_0.Actions, ActionFactory, VERSION_400, fill_nullables=True)
        GenericFactoryAvro.register_factory(
            reports_4_0_0.Actions, ActionFactory, VERSION_400, fill_nullables=False)

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

    def test_migrate_rd_clinical_report(self):
        # creates a random clinical report RD for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportRD, VERSION_61, fill_nullables=True
        ).create(interpretationRequestVersion='1')  # we need to enforce that it can be cast to int

        self._validate(old_instance)
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

        halfway_instance = MigrateReports500To400().migrate_clinical_report_rd(old_instance=old_instance)

        self.assertTrue(isinstance(halfway_instance, self.halfway_model.ClinicalReportRD))

        self._validate(halfway_instance)
        self._check_variant_coordinates(
            old_variants=old_instance.variants,
            new_variants=halfway_instance.candidateVariants,
        )

        new_instance = MigrateReports400To300().migrate_clinical_report_rd(old_instance=halfway_instance)
        self.assertIsInstance(new_instance, self.new_model.ClinicalReportRD)
        self._validate(new_instance)
        self._check_variant_coordinates_4_3(
            old_variants=halfway_instance.candidateVariants,
            new_variants=new_instance.candidateVariants,
        )

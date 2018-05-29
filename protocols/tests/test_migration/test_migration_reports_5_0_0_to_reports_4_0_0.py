import factory.fuzzy
from random import randint

from protocols import reports_4_0_0
from protocols import reports_5_0_0
from protocols.util.dependency_manager import VERSION_61
from protocols.util.dependency_manager import VERSION_500
from protocols.util.dependency_manager import VERSION_400
from protocols.util.factories.avro_factory import FactoryAvro
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_5_0_0_to_reports_4_0_0 import MigrateReports500To400


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
    new_model = reports_4_0_0

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

    def test_migrate_analysis_panel(self):
        old_panel = GenericFactoryAvro.get_factory_avro(
            self.old_model.AdditionalAnalysisPanel, VERSION_61, fill_nullables=True
        ).create()
        new_panel = MigrateReports500To400().migrate_analysis_panel(old_panel=old_panel)
        self.assertTrue(new_panel.validate(new_panel.toJsonDict()))

    def test_migrate_genomic_entity_to_feature(self):
        old_entity = GenericFactoryAvro.get_factory_avro(self.old_model.GenomicEntity, VERSION_61, fill_nullables=True).create()

        valid_genomic_features = [
            self.old_model.GenomicEntityType.regulatory_region,
            self.old_model.GenomicEntityType.gene,
            self.old_model.GenomicEntityType.transcript,
        ]
        if old_entity.type not in valid_genomic_features:
            old_entity.type = valid_genomic_features[randint(0, len(valid_genomic_features)-1)]

        entity_type = old_entity.type
        feature_type_map = {
            self.old_model.GenomicEntityType.regulatory_region: self.new_model.FeatureTypes.RegulatoryRegion,
            self.old_model.GenomicEntityType.gene: self.new_model.FeatureTypes.Gene,
            self.old_model.GenomicEntityType.transcript: self.new_model.FeatureTypes.Transcript,
        }
        expected_feature_type = feature_type_map.get(entity_type)
        new_feature = MigrateReports500To400().migrate_genomic_entity_to_feature(old_entity)
        self.assertTrue(isinstance(new_feature, self.new_model.GenomicFeature))
        self._validate(new_feature)
        self.assertEqual(new_feature.featureType, expected_feature_type)

    def test_migrate_report_event(self):
        old_report_event = GenericFactoryAvro.get_factory_avro(self.old_model.ReportEvent, VERSION_61, fill_nullables=True).create()
        #################################################
        # TODO(Greg): Remove this when IP-1394 is resolved
        valid_tiers = ["TIER1", "TIER2", "TIER3", "NONE"]
        if old_report_event.tier not in valid_tiers:
            old_report_event.tier = valid_tiers[randint(0, len(valid_tiers)-1)]
        #################################################

        valid_genomic_features = [
            self.old_model.GenomicEntityType.regulatory_region,
            self.old_model.GenomicEntityType.gene,
            self.old_model.GenomicEntityType.transcript,
        ]
        entity = old_report_event.genomicEntities[0]
        if entity.type not in valid_genomic_features:
            entity.type = valid_genomic_features[randint(0, len(valid_genomic_features)-1)]

        new_report_event = MigrateReports500To400().migrate_report_event(old_report_event=old_report_event)
        self.assertTrue(isinstance(new_report_event, self.new_model.ReportEvent))
        self._validate(new_report_event)

    def test_migrate_reported_variant(self):
        old_reported_variant = GenericFactoryAvro.get_factory_avro(self.old_model.ReportedVariant, VERSION_61, fill_nullables=True).create()

        #################################################
        # TODO(Greg): Remove this when IP-1394 is resolved
        valid_tiers = ["TIER1", "TIER2", "TIER3", "NONE"]
        for re in old_reported_variant.reportEvents:
            if re.tier not in valid_tiers:
                re.tier = valid_tiers[randint(0, len(valid_tiers)-1)]
        #################################################

        valid_genomic_features = [
            self.old_model.GenomicEntityType.regulatory_region,
            self.old_model.GenomicEntityType.gene,
            self.old_model.GenomicEntityType.transcript,
        ]
        for re in old_reported_variant.reportEvents:
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
        for vc in old_reported_variant.variantCalls:
            if vc.zygosity not in valid_genotypes:
                vc.zygosity = valid_genotypes[randint(0, len(valid_genotypes)-1)]

        new_reported_variant = MigrateReports500To400().migrate_reported_variant(old_reported_variant=old_reported_variant)
        self.assertTrue(isinstance(new_reported_variant, self.new_model.ReportedVariant))
        self._validate(new_reported_variant)

    def test_migrate_variant_call_to_called_genotype(self):
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.VariantCall, VERSION_61, fill_nullables=True
        ).create()

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

        if old_instance.zygosity not in valid_genotypes:
            old_instance.zygosity = valid_genotypes[randint(0, len(valid_genotypes)-1)]

        new_instance = MigrateReports500To400().migrate_variant_call_to_called_genotype(variant_call=old_instance)
        self.assertTrue(isinstance(new_instance, self.new_model.CalledGenotype))
        self._validate(new_instance)

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

        new_instance = MigrateReports500To400().migrate_clinical_report_rd(old_instance=old_instance)

        self.assertTrue(isinstance(new_instance, self.new_model.ClinicalReportRD))

        self._validate(new_instance)
        self._check_variant_coordinates(
            old_variants=old_instance.variants,
            new_variants=new_instance.candidateVariants,
        )


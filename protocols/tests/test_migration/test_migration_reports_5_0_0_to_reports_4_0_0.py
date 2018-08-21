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


class TestMigrateReports5To400(TestCaseMigration):

    old_model = reports_5_0_0
    new_model = reports_4_0_0

    def setUp(self):

        valid_tiers = [self.old_model.Tier.TIER1, self.old_model.Tier.TIER2,
                       self.old_model.Tier.TIER3, self.old_model.Tier.NONE]

        # registers factories to ensure that tiers in report events are only valid ones
        class ReportEventFactoryNulls(FactoryAvro):
            def __init__(self, *args, **kwargs):
                super(ReportEventFactoryNulls, self).__init__(*args, **kwargs)

            class Meta:
                model = self.old_model.ReportEvent
            _version = VERSION_61
            _fill_nullables = True
            tier = factory.fuzzy.FuzzyChoice(valid_tiers)
        GenericFactoryAvro.register_factory(self.old_model.ReportEvent, ReportEventFactoryNulls, VERSION_61, True)

        class ReportEventFactory(FactoryAvro):
            def __init__(self, *args, **kwargs):
                super(ReportEventFactory, self).__init__(*args, **kwargs)

            class Meta:
                model = self.old_model.ReportEvent
            _version = VERSION_61
            _fill_nullables = False
            tier = factory.fuzzy.FuzzyChoice(valid_tiers)
        GenericFactoryAvro.register_factory(self.old_model.ReportEvent, ReportEventFactory, VERSION_61, False)

        valid_genomic_features = [self.old_model.GenomicEntityType.regulatory_region,
                                  self.old_model.GenomicEntityType.gene, self.old_model.GenomicEntityType.transcript]

        class GenomicEntityFactoryNulls(FactoryAvro):
            def __init__(self, *args, **kwargs):
                super(GenomicEntityFactoryNulls, self).__init__(*args, **kwargs)

            class Meta:
                model = self.old_model.GenomicEntity
            _version = VERSION_61
            _fill_nullables = True
            type = factory.fuzzy.FuzzyChoice(valid_genomic_features)
        GenericFactoryAvro.register_factory(self.old_model.GenomicEntity, GenomicEntityFactoryNulls, VERSION_61, True)

        class GenomicEntityFactory(FactoryAvro):
            def __init__(self, *args, **kwargs):
                super(GenomicEntityFactory, self).__init__(*args, **kwargs)

            class Meta:
                model = self.old_model.GenomicEntity
            _version = VERSION_61
            _fill_nullables = False
            type = factory.fuzzy.FuzzyChoice(valid_genomic_features)
        GenericFactoryAvro.register_factory(self.old_model.GenomicEntity, GenomicEntityFactory, VERSION_61, False)

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

        class VariantCallFactoryNulls(FactoryAvro):
            def __init__(self, *args, **kwargs):
                super(VariantCallFactoryNulls, self).__init__(*args, **kwargs)

            class Meta:
                model = self.old_model.VariantCall

            _version = VERSION_61
            _fill_nullables = True
            zygosity = factory.fuzzy.FuzzyChoice(valid_genotypes)
        GenericFactoryAvro.register_factory(self.old_model.VariantCall, VariantCallFactoryNulls, VERSION_61, True)

        class VariantCallFactory(FactoryAvro):
            def __init__(self, *args, **kwargs):
                super(VariantCallFactory, self).__init__(*args, **kwargs)

            class Meta:
                model = self.old_model.VariantCall

            _version = VERSION_61
            _fill_nullables = False
            zygosity = factory.fuzzy.FuzzyChoice(valid_genotypes)
        GenericFactoryAvro.register_factory(self.old_model.VariantCall, VariantCallFactory, VERSION_61, False)

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
        new_report_event = MigrateReports500To400().migrate_report_event(old_report_event=old_report_event)
        self.assertTrue(isinstance(new_report_event, self.new_model.ReportEvent))
        self._validate(new_report_event)

    def test_migrate_reported_variant(self):
        old_reported_variant = GenericFactoryAvro.get_factory_avro(self.old_model.ReportedVariant, VERSION_61, fill_nullables=True).create()
        new_reported_variant = MigrateReports500To400().migrate_reported_variant(old_reported_variant=old_reported_variant)
        self.assertTrue(isinstance(new_reported_variant, self.new_model.ReportedVariant))
        self._validate(new_reported_variant)

    def test_migrate_variant_call_to_called_genotype(self):
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.VariantCall, VERSION_61, fill_nullables=True
        ).create()
        new_instance = MigrateReports500To400().migrate_variant_call_to_called_genotype(variant_call=old_instance)
        self.assertTrue(isinstance(new_instance, self.new_model.CalledGenotype))
        self._validate(new_instance)

    def test_migrate_rd_clinical_report(self, fill_nullables=True):
        # creates a random clinical report RD for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportRD, VERSION_61, fill_nullables=fill_nullables
        ).create(interpretationRequestVersion=1)

        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        new_instance = MigrateReports500To400().migrate_clinical_report_rd(old_instance=old_instance)
        self.assertTrue(isinstance(new_instance, self.new_model.ClinicalReportRD))
        self._validate(new_instance)
        if fill_nullables:
            self._check_variant_coordinates(
                old_variants=old_instance.variants,
                new_variants=new_instance.candidateVariants,
            )

    def test_migrate_rd_clinical_report_nullables_false(self):
        self.test_migrate_rd_clinical_report(fill_nullables=False)

    def test_migrate_rd_interpretation_request(self, fill_nullables=True):
        # creates a random clinical report RD for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretationRequestRD, VERSION_61, fill_nullables=fill_nullables
        ).create(interpretationRequestVersion=1)

        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        old_ig = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_61, fill_nullables=fill_nullables
        ).create(interpretationRequestVersion=1, interpretationRequestId=old_instance.interpretationRequestId)

        self._validate(old_ig)
        if fill_nullables:
            self._check_non_empty_fields(old_ig)

        new_instance = MigrateReports500To400().migrate_interpretation_request_rd(
            old_instance=old_instance, old_ig=old_ig, cip='nextcode')
        self.assertTrue(isinstance(new_instance, self.new_model.InterpretationRequestRD))
        self._validate(new_instance)
        if fill_nullables:
            self._check_variant_coordinates(
                old_variants=old_ig.variants,
                new_variants=new_instance.tieredVariants,
            )

    def test_migrate_rd_interpretation_request_nulls(self):
        self.test_migrate_rd_interpretation_request(fill_nullables=False)


import factory.fuzzy
from random import randint

from protocols import reports_4_0_0
from protocols import reports_5_0_0
from protocols.util.dependency_manager import VERSION_61
from protocols.util.factories.avro_factory import FactoryAvro
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration import MigrateReports500To400, BaseMigration


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

        # ensures that IR RD always have a pedigree
        class InterpretationRequestRDFactory(FactoryAvro):
            def __init__(self, *args, **kwargs):
                super(InterpretationRequestRDFactory, self).__init__(*args, **kwargs)

            class Meta:
                model = self.old_model.InterpretationRequestRD
            _version = VERSION_61
            _fill_nullables = False
            pedigree = GenericFactoryAvro.get_factory_avro(
                self.old_model.Pedigree, VERSION_61, fill_nullables=_fill_nullables).create()
        GenericFactoryAvro.register_factory(
            self.old_model.InterpretationRequestRD, InterpretationRequestRDFactory, VERSION_61, False)

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
        new_panel = MigrateReports500To400()._migrate_analysis_panel(old_panel=old_panel)
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
        new_feature = MigrateReports500To400()._migrate_genomic_entity_to_feature(old_entity)
        self.assertTrue(isinstance(new_feature, self.new_model.GenomicFeature))
        self._validate(new_feature)
        self.assertEqual(new_feature.featureType, expected_feature_type)

    def test_migrate_report_event(self):
        old_report_event = GenericFactoryAvro.get_factory_avro(self.old_model.ReportEvent, VERSION_61, fill_nullables=True).create()
        new_report_event = BaseMigration.convert_class(reports_4_0_0.ReportEvent, old_report_event)
        new_report_event = MigrateReports500To400()._migrate_report_event((old_report_event, new_report_event))
        self.assertTrue(isinstance(new_report_event, self.new_model.ReportEvent))
        self._validate(new_report_event)

    def test_migrate_reported_variant(self):
        old_reported_variant = GenericFactoryAvro.get_factory_avro(self.old_model.ReportedVariant, VERSION_61, fill_nullables=True).create()
        new_reported_variant = MigrateReports500To400()._migrate_reported_variant(old_reported_variant=old_reported_variant)
        self.assertTrue(isinstance(new_reported_variant, self.new_model.ReportedVariant))
        self._validate(new_reported_variant)

    def test_migrate_variant_call_to_called_genotype(self):
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.VariantCall, VERSION_61, fill_nullables=True
        ).create()
        new_instance = MigrateReports500To400()._migrate_variant_call_to_called_genotype(variant_call=old_instance)
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

    def test_migrate_rd_exit_questionnaire(self, fill_nullables=True):
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.RareDiseaseExitQuestionnaire, VERSION_61, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        new_instance = MigrateReports500To400().migrate_exit_questionnaire_rd(old_instance=old_instance)
        self.assertTrue(isinstance(new_instance, self.new_model.RareDiseaseExitQuestionnaire))
        self._validate(new_instance)

    def test_migrate_rd_exit_questionnaire_nullables_false(self):
        self.test_migrate_rd_exit_questionnaire(fill_nullables=False)

    def test_migrate_interpretation_request_cancer_plus_cancer_interpreted_genome(self, fill_nullables=True):
        ir_c_5 = self.get_valid_object(object_type=self.old_model.CancerInterpretationRequest,
                                       version=self.version_6_1, fill_nullables=fill_nullables)
        ir_c_5.additionalInfo = {
            'interpretGenome': 'True',
            'analysisUri': 'blah.com',
            'analysisVersion': '1',
            'tieringVersion': '1'
        }
        ig_c_5 = self.get_valid_object(object_type=self.old_model.CancerInterpretedGenome,
                                       version=self.version_6_1, fill_nullables=fill_nullables)
        ir_c_4 = MigrateReports500To400().migrate_interpretation_request_cancer_plus_cancer_interpreted_genome(
            old_instance=ir_c_5, old_interpreted_genome=ig_c_5
        )
        self.assertIsInstance(ir_c_4, self.new_model.CancerInterpretationRequest)
        self.assertTrue(ir_c_4.validate(ir_c_4.toJsonDict()))

    def test_migrate_interpretation_request_cancer_plus_cancer_interpreted_genome_nulls(self):
        self.test_migrate_interpretation_request_cancer_plus_cancer_interpreted_genome(fill_nullables=False)

    def test_migrate_variant(self):
        rvc_5 = self.get_valid_object(object_type=self.old_model.ReportedVariantCancer, version=self.version_6_1)
        rsv_4 = MigrateReports500To400()._migrate_reported_variant_cancer_to_reported_somatic_variant(old_variant=rvc_5)
        self.assertIsInstance(rsv_4, self.new_model.ReportedSomaticVariants)
        self.assertTrue(rsv_4.validate(rsv_4.toJsonDict()))

    def test_migrate_reported_variant_cancer(self):
        rvc_5 = self.get_valid_object(object_type=self.old_model.ReportedVariantCancer, version=self.version_6_1)
        rvc_4 = MigrateReports500To400()._migrate_reported_variant_cancer(old_rvc=rvc_5)
        self.assertIsInstance(rvc_4, self.new_model.ReportedVariantCancer)
        self.assertTrue(rvc_4.validate(rvc_4.toJsonDict()))

    def test_migrate_genomic_entities_to_genomic_feature_cancer(self):
        ge_5 = self.get_valid_object(object_type=self.old_model.GenomicEntity, version=self.version_6_1)
        test_ref_seq_transcript_id = "test_refSeqTranscriptId"
        test_ref_seq_protein_id = "test_refSeqProteinId"
        ge_5.otherIds["refSeqTranscriptId"] = test_ref_seq_transcript_id
        ge_5.otherIds["refSeqProteinId"] = test_ref_seq_protein_id
        gfc_4 = MigrateReports500To400()._migrate_genomic_entities_to_genomic_feature_cancer(genomic_entities=[ge_5])
        self.assertIsInstance(gfc_4, self.new_model.GenomicFeatureCancer)
        self.assertTrue(gfc_4.validate(gfc_4.toJsonDict()))
        self.assertEqual(gfc_4.refSeqProteinId, test_ref_seq_protein_id)
        self.assertEqual(gfc_4.refSeqTranscriptId, test_ref_seq_transcript_id)

    def test_migrate_variant_consequence_to_so_term(self):
        vc_5 = self.get_valid_object(object_type=self.old_model.VariantConsequence, version=self.version_6_1)
        so_4 = MigrateReports500To400()._migrate_variant_consequence_to_so_term(vc=vc_5)
        self.assertIsInstance(so_4, self.new_model.SoTerm)
        self.assertTrue(so_4.validate(so_4.toJsonDict()))
        self.assertEqual(so_4.name, vc_5.name)
        self.assertEqual(so_4.id, vc_5.id)

    def test_migrate_rd_interpreted_genome(self, fill_nullables=True):
        # creates a random clinical report RD for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_61, fill_nullables=fill_nullables
        ).create(interpretationRequestVersion=1)

        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        new_instance = MigrateReports500To400().migrate_interpreted_genome_rd(old_instance=old_instance)
        self.assertTrue(isinstance(new_instance, self.new_model.InterpretedGenomeRD))
        self._validate(new_instance)
        if fill_nullables:
            self._check_variant_coordinates(
                old_variants=old_instance.variants,
                new_variants=new_instance.reportedVariants,
            )

    def test_migrate_rd_interpreted_genome_nullables_false(self):
        self.test_migrate_rd_interpreted_genome(fill_nullables=False)

    def test_migrate_rd_interpretation_request(self, fill_nullables=True):
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretationRequestRD, VERSION_61, fill_nullables=fill_nullables
        ).create(interpretationRequestVersion=1)
        old_instance.additionalInfo = {}
        old_instance.additionalInfo['cellbaseVersion'] = '1.0'
        old_instance.additionalInfo['tieringVersion'] = '1.0'
        old_instance.additionalInfo['analysisReturnUri'] = 'uri.com'

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
            old_instance=old_instance, old_ig=old_ig)
        self.assertTrue(isinstance(new_instance, self.new_model.InterpretationRequestRD))
        self._validate(new_instance)
        if fill_nullables:
            self._check_variant_coordinates(
                old_variants=old_ig.variants,
                new_variants=new_instance.tieredVariants,
            )

    def test_migrate_rd_interpretation_request_nulls(self):
        self.test_migrate_rd_interpretation_request(fill_nullables=False)

    def test_migrate_cancer_interpreted_genome(self, fill_nullables=True):
        # creates a random clinical report RD for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.CancerInterpretedGenome, VERSION_61, fill_nullables=fill_nullables
        ).create(interpretationRequestVersion=1)

        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        new_instance = MigrateReports500To400().migrate_cancer_interpreted_genome(old_instance=old_instance)
        self.assertTrue(isinstance(new_instance, self.new_model.CancerInterpretedGenome))
        self._validate(new_instance)

    def test_migrate_cancer_interpreted_genome_nullables_false(self):
        self.test_migrate_cancer_interpreted_genome(fill_nullables=False)

    def test_migrate_cancer_clinical_report(self, fill_nullables=True):
        cr_c_5 = self.get_valid_object(object_type=self.old_model.ClinicalReportCancer, version=self.version_6_1, fill_nullables=fill_nullables)
        cr_c_4 = MigrateReports500To400().migrate_cancer_clinical_report(old_instance=cr_c_5)
        self.assertIsInstance(cr_c_4, self.new_model.ClinicalReportCancer)
        self.assertTrue(cr_c_4.validate(cr_c_4.toJsonDict()))

    def test_migrate_cancer_clinical_report_nullables_false(self):
        self.test_migrate_rd_clinical_report(fill_nullables=False)


import random
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
import factory.fuzzy
from protocols import reports_4_0_0
from protocols import reports_5_0_0
from protocols.migration.migration_reports_400_to_reports_500 import MigrateReports400To500
from protocols.util.dependency_manager import VERSION_400
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.util.factories.avro_factory import FactoryAvro


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


class TestMigrateReports4To500(TestCaseMigration):

    old_model = reports_4_0_0
    new_model = reports_5_0_0

    def setUp(self):
        GenericFactoryAvro.register_factory(
            reports_4_0_0.Actions, ActionFactory, VERSION_400, fill_nullables=True)
        GenericFactoryAvro.register_factory(
            reports_4_0_0.Actions, ActionFactory, VERSION_400, fill_nullables=False)

    def _check_variant_coordinates(self, old_variants, new_variants, assembly):
        for old_variant, new_variant in zip(old_variants, new_variants):
            self.assertEqual(old_variant.reference, new_variant.variantCoordinates.reference)
            self.assertEqual(old_variant.alternate, new_variant.variantCoordinates.alternate)
            self.assertEqual(old_variant.position, new_variant.variantCoordinates.position)
            self.assertEqual(old_variant.chromosome, new_variant.variantCoordinates.chromosome)
            self.assertEqual(assembly, new_variant.variantCoordinates.assembly)

    def test_migrate_cancer_clinical_report(self):

        # creates a random clinical report cancer for testing filling null values
        cr_c_400 = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportCancer, VERSION_400, fill_nullables=True
        ).create(interpretationRequestVersion='1')  # we need to enforce that it can be cast to int
        valid_cancer_origins = ['germline_variant', 'somatic_variant']
        if cr_c_400.candidateVariants:
            for candidate_variant in cr_c_400.candidateVariants:
                if candidate_variant.alleleOrigins[0] not in valid_cancer_origins:
                    candidate_variant.alleleOrigins[0] = random.choice(valid_cancer_origins)
        self._validate(cr_c_400)
        self._check_non_empty_fields(cr_c_400)

        assembly = 'grch38'
        participant_id = "no_one"
        sample_ids = {
            'germline_variant': 'germline1',
            'somatic_variant': 'somatic1'
        }
        migrated_cir_500 = MigrateReports400To500().migrate_cancer_clinical_report(
            cr_c_400, assembly=assembly, participant_id=participant_id, sample_ids=sample_ids
        )
        self._validate(migrated_cir_500)
        self._check_non_empty_fields(migrated_cir_500,
                                     exclusions=["genomicChanges", "references", "actionType", "otherIds",
                                                 "groupOfVariants", "score", "vendorSpecificScores",
                                                 "variantClassification", "fdp50", "recurrentlyReported", "others",
                                                 "phaseSet"])

        self._check_variant_coordinates(
            [variant.reportedVariantCancer for variant in cr_c_400.candidateVariants],
            migrated_cir_500.variants,
            reports_5_0_0.Assembly.GRCh38
        )

        # creates a random clinical report cancer for testing not filling null values
        cr_c_400 = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportCancer, VERSION_400, fill_nullables=False
        ).create(interpretationRequestVersion='1')
        if cr_c_400.candidateVariants:
            for candidate_variant in cr_c_400.candidateVariants:
                if candidate_variant.alleleOrigins[0] not in valid_cancer_origins:
                    candidate_variant.alleleOrigins[0] = random.choice(valid_cancer_origins)
        self._validate(cr_c_400)

        assembly = 'hg19'
        participant_id = "no_one"
        sample_ids = {
            'germline_variant': 'germline1',
            'somatic_variant': 'somatic1'
        }
        migrated_cir_500 = MigrateReports400To500().migrate_cancer_clinical_report(
            cr_c_400, assembly=assembly, participant_id=participant_id, sample_ids=sample_ids
        )
        self._validate(migrated_cir_500)

        self.assertTrue(cr_c_400.candidateVariants is None)
        self.assertTrue(migrated_cir_500.variants is None)

    def test_migrate_cancer_interpreted_genome(self):

        # creates a random clinical report cancer for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.CancerInterpretedGenome, VERSION_400, fill_nullables=True
        ).create()
        valid_cancer_origins = ['germline_variant', 'somatic_variant']
        for reported_variant in old_instance.reportedVariants:
            if reported_variant.alleleOrigins[0] not in valid_cancer_origins:
                reported_variant.alleleOrigins[0] = random.choice(valid_cancer_origins)
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        assembly = 'grch38'
        participant_id = "no_one"
        sample_ids = {
            'germline_variant': 'germline1',
            'somatic_variant': 'somatic1'
        }
        interpretation_request_version = 1
        interpretation_service = 'testing'
        new_instance = MigrateReports400To500().migrate_cancer_interpreted_genome(
            old_instance, assembly=assembly, participant_id=participant_id, sample_ids=sample_ids,
            interpretation_request_version=interpretation_request_version,
            interpretation_service=interpretation_service
        )
        self._validate(new_instance)
        self._check_non_empty_fields(new_instance,
                                     exclusions=["genomicChanges", "references", "actionType", "otherIds",
                                                 "groupOfVariants", "score", "vendorSpecificScores",
                                                 "variantClassification", "fdp50", "recurrentlyReported", "others",
                                                 "phaseSet"])

        self._check_variant_coordinates(
            [variant.reportedVariantCancer for variant in old_instance.reportedVariants],
            new_instance.variants,
            reports_5_0_0.Assembly.GRCh38
        )

        # creates a random clinical report cancer for testing not filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.CancerInterpretedGenome, VERSION_400, fill_nullables=False
        ).create()
        self._validate(old_instance)
        valid_cancer_origins = ['germline_variant', 'somatic_variant']
        for reported_variant in old_instance.reportedVariants:
            if reported_variant.alleleOrigins[0] not in valid_cancer_origins:
                reported_variant.alleleOrigins[0] = random.choice(valid_cancer_origins)

        assembly = 'hg19'
        participant_id = "no_one"
        sample_ids = {
            'germline_variant': 'germline1',
            'somatic_variant': 'somatic1'
        }
        interpretation_request_version = 1
        interpretation_service = 'testing'
        new_instance = MigrateReports400To500().migrate_cancer_interpreted_genome(
            old_instance, assembly=assembly, participant_id=participant_id, sample_ids=sample_ids,
            interpretation_request_version=interpretation_request_version,
            interpretation_service=interpretation_service
        )
        self._validate(new_instance)
        self._check_variant_coordinates(
            [variant.reportedVariantCancer for variant in old_instance.reportedVariants],
            new_instance.variants,
            reports_5_0_0.Assembly.GRCh37
        )

    def test_migrate_cancer_interpretation_request_to_cancer_interpreted_genome(self):

        # creates a random clinical report cancer for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.CancerInterpretationRequest, VERSION_400, fill_nullables=True
        ).create()

        valid_cancer_origins = ['germline_variant', 'somatic_variant']
        for tiered_variant in old_instance.tieredVariants:
            if tiered_variant.alleleOrigins[0] not in valid_cancer_origins:
                tiered_variant.alleleOrigins[0] = random.choice(valid_cancer_origins)

        old_instance.cancerParticipant.tumourSamples = [old_instance.cancerParticipant.tumourSamples[0]]
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        assembly = 'grch38'
        interpretation_service = 'testing'
        new_instance = MigrateReports400To500().migrate_cancer_interpretation_request_to_cancer_interpreted_genome(
            old_instance, assembly=assembly,
            interpretation_service=interpretation_service,
            reference_database_versions={'dbSnp': 'rs12345'},
            software_versions={'intogen': '1.5'},
            report_url="blablabla.blah",
            comments=["bla", "bla!", "bla?"]
        )
        self._validate(new_instance)
        self._check_non_empty_fields(new_instance,
                                     exclusions=["genomicChanges", "references", "actionType", "otherIds",
                                                 "groupOfVariants", "score", "vendorSpecificScores",
                                                 "variantClassification", "fdp50", "recurrentlyReported", "others",
                                                 "phaseSet"])

        self._check_variant_coordinates(
            [variant.reportedVariantCancer for variant in old_instance.tieredVariants],
            new_instance.variants,
            reports_5_0_0.Assembly.GRCh38
        )

        # creates a random clinical report cancer for testing not filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.CancerInterpretationRequest, VERSION_400, fill_nullables=False
        ).create()
        for tiered_variant in old_instance.tieredVariants:
            if tiered_variant.alleleOrigins[0] not in valid_cancer_origins:
                tiered_variant.alleleOrigins[0] = random.choice(valid_cancer_origins)
        old_instance.cancerParticipant.tumourSamples = [old_instance.cancerParticipant.tumourSamples[0]]
        self._validate(old_instance)

        assembly = 'grCH37'
        interpretation_service = 'testing'
        new_instance = MigrateReports400To500().migrate_cancer_interpretation_request_to_cancer_interpreted_genome(
            old_instance, assembly=assembly,
            interpretation_service=interpretation_service,
            reference_database_versions={},
            software_versions={}
        )
        self._validate(new_instance)
        self._check_variant_coordinates(
            [variant.reportedVariantCancer for variant in old_instance.tieredVariants],
            new_instance.variants,
            reports_5_0_0.Assembly.GRCh37
        )

    def test_migrate_rd_clinical_report(self):

        # creates a random clinical report cancer for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportRD, VERSION_400, fill_nullables=True
        ).create(interpretationRequestVersion='1')  # we need to enforce that it can be cast to int
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        assembly = 'grch38'
        new_instance = MigrateReports400To500().migrate_clinical_report_rd(
            old_instance, assembly=assembly
        )
        self._validate(new_instance)
        self._check_non_empty_fields(new_instance,
                                     exclusions=["alleleFrequencies", "genomicChanges", "proteinChanges",
                                                 "cdnaChanges", "dbSnpId", "cosmicIds", "clinVarIds",
                                                 "variantConsequences", "drugResponseClassification",
                                                 "functionalEffect", "traitAssociation", "tumorigenesisClassification",
                                                 "clinicalSignificance", "variantAttributes", "vaf"])
        self._check_variant_coordinates(
            old_instance.candidateVariants,
            new_instance.variants,
            reports_5_0_0.Assembly.GRCh38
        )

        # creates a random clinical report cancer for testing not filling null values
        cr_c_400 = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportRD, VERSION_400, fill_nullables=False
        ).create(interpretationRequestVersion='1')
        self._validate(cr_c_400)

        assembly = 'hg19'
        new_instance = MigrateReports400To500().migrate_clinical_report_rd(
            cr_c_400, assembly=assembly
        )
        self._validate(new_instance)

        self.assertTrue(cr_c_400.candidateVariants is None)
        self.assertTrue(new_instance.variants is None)

    def test_migrate_rd_interpreted_genome(self):

        # creates a random clinical report cancer for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_400, fill_nullables=True
        ).create()  # we need to enforce that it can be cast to int
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        assembly = 'grch38'
        new_instance = MigrateReports400To500().migrate_interpreted_genome_rd(
            old_instance, assembly=assembly, interpretation_request_version=1
        )
        self._validate(new_instance)
        self._check_non_empty_fields(new_instance,
                                     exclusions=["alleleFrequencies", "genomicChanges", "proteinChanges",
                                                 "cdnaChanges", "dbSnpId", "cosmicIds", "clinVarIds",
                                                 "variantConsequences", "drugResponseClassification",
                                                 "functionalEffect", "traitAssociation", "tumorigenesisClassification",
                                                 "clinicalSignificance", "variantAttributes", "vaf"])
        self._check_variant_coordinates(
            old_instance.reportedVariants,
            new_instance.variants,
            reports_5_0_0.Assembly.GRCh38
        )

        # creates a random RD interpreted genome for testing not filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_400, fill_nullables=False
        ).create()
        self._validate(old_instance)

        assembly = 'hg19'
        new_instance = MigrateReports400To500().migrate_interpreted_genome_rd(
            old_instance, assembly=assembly, interpretation_request_version=1
        )
        self._validate(new_instance)

        self._check_variant_coordinates(
            old_instance.reportedVariants,
            new_instance.variants,
            reports_5_0_0.Assembly.GRCh37
        )

    def test_migrate_interpretation_request_rd_to_interpreted_genome_rd(self):

        # creates a random clinical report cancer for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretationRequestRD, VERSION_400, fill_nullables=True
        ).create()  # we need to enforce that it can be cast to int
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        assembly = 'grch38'
        interpretation_service = "testing"
        new_instance = MigrateReports400To500().migrate_interpretation_request_rd_to_interpreted_genome_rd(
            old_instance, assembly=assembly, interpretation_service=interpretation_service,
            reference_database_versions={'dbSnp': 'rs12345'},
            software_versions={'intogen': '1.5'},
            report_url="blablabla.blah",
            comments=["bla", "bla!", "bla?"]
        )
        self._validate(new_instance)
        self._check_non_empty_fields(new_instance,
                                     exclusions=["alleleFrequencies", "genomicChanges", "proteinChanges",
                                                 "cdnaChanges", "dbSnpId", "cosmicIds", "clinVarIds",
                                                 "variantConsequences", "drugResponseClassification",
                                                 "functionalEffect", "traitAssociation", "tumorigenesisClassification",
                                                 "clinicalSignificance", "variantAttributes", "vaf"])
        self._check_variant_coordinates(
            old_instance.tieredVariants,
            new_instance.variants,
            reports_5_0_0.Assembly.GRCh38
        )
        self.assertEqual(old_instance.tieringVersion, new_instance.softwareVersions['tiering'])

        # creates a random clinical report cancer for testing not filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretationRequestRD, VERSION_400, fill_nullables=False
        ).create()
        self._validate(old_instance)

        assembly = 'hg19'
        new_instance = MigrateReports400To500().migrate_interpretation_request_rd_to_interpreted_genome_rd(
            old_instance, assembly=assembly, interpretation_service=interpretation_service,
            reference_database_versions={'dbSnp': 'rs12345'},
            software_versions={'intogen': '1.5'},
            report_url="blablabla.blah",
            comments=["bla", "bla!", "bla?"]
        )
        self._validate(new_instance)

        self._check_variant_coordinates(
            old_instance.tieredVariants,
            new_instance.variants,
            reports_5_0_0.Assembly.GRCh37
        )

    def test_migrate_interpretation_request_rd(self):

        # tests with all nullable fields being filled
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretationRequestRD, VERSION_400, fill_nullables=True
        ).create()
        if old_instance.pedigree.members:
            for member in old_instance.pedigree.members:
                if member.disorderList:
                    for disorder in member.disorderList:
                        disorder.ageOfOnset = "1.5"
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        migrated_instance = MigrateReports400To500().migrate_interpretation_request_rd(
            old_instance=old_instance, assembly='GRCh38'
        )
        self._validate(migrated_instance)
        for other_file in migrated_instance.otherFiles.values():
            self.assertIsInstance(other_file, self.new_model.File)

        # test with all nullable fields being null
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretationRequestRD, VERSION_400, fill_nullables=False
        ).create()
        self._validate(old_instance)

        migrated_instance = MigrateReports400To500().migrate_interpretation_request_rd(
            old_instance=old_instance, assembly='GRCh38'
        )
        self._validate(migrated_instance)
        if migrated_instance.otherFiles is not None:
            for other_file in migrated_instance.otherFiles.values():
                self.assertIsInstance(other_file, self.new_model.File)

    def test_migrate_cancer_interpretation_request(self):
        """
        Test passing with ILMN-8308-1 cancer IR
        """
        # tests with all nullable fields being filled
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.CancerInterpretationRequest, VERSION_400, fill_nullables=True
        ).create()  # we need to enforce that it can be cast to int
        valid_cancer_origins = ['germline_variant', 'somatic_variant']
        for tiered_variant in old_instance.tieredVariants:
            if tiered_variant.alleleOrigins[0] not in valid_cancer_origins:
                tiered_variant.alleleOrigins[0] = random.choice(valid_cancer_origins)
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)
        migrated_instance = MigrateReports400To500().migrate_cancer_interpretation_request(
            old_instance=old_instance, assembly='GRCh38'
        )
        self._validate(migrated_instance)

        # test with all nullable fields being null
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.CancerInterpretationRequest, VERSION_400, fill_nullables=False
        ).create()  # we need to enforce that it can be cast to int
        for tiered_variant in old_instance.tieredVariants:
            if tiered_variant.alleleOrigins[0] not in valid_cancer_origins:
                tiered_variant.alleleOrigins[0] = random.choice(valid_cancer_origins)
        old_instance.cancerParticipant.LDPCode = "needs to be filled"
        self._validate(old_instance)
        migrated_instance = MigrateReports400To500().migrate_cancer_interpretation_request(
            old_instance=old_instance, assembly='GRCh38'
        )
        self._validate(migrated_instance)

    def test_json_serialization(self):
        from protocols.util.dependency_manager import VERSION_400
        from protocols.util.factories.avro_factory import GenericFactoryAvro
        from protocols.reports_4_0_0 import CancerInterpretationRequest as CancerInterpretationRequest_4_0_0
        cir_v4 = GenericFactoryAvro.get_factory_avro(clazz=CancerInterpretationRequest_4_0_0,
                                                            version=VERSION_400, fill_nullables=True).create()
        cir_v4.validate(cir_v4.toJsonDict())
        cir_v4_json = cir_v4.toJsonDict()

        cir_v4_from_json = CancerInterpretationRequest_4_0_0.fromJsonDict(cir_v4_json)
        cir_v4_from_json.validate(cir_v4_from_json.toJsonDict())

    def test_migrate_rare_disease_exit_questionnaire(self):
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.RareDiseaseExitQuestionnaire, VERSION_400, fill_nullables=True
        ).create()
        self.assertIsInstance(old_instance, self.old_model.RareDiseaseExitQuestionnaire)
        self._validate(old_instance)
        old_json = old_instance.toJsonDict()
        new_instance = self.new_model.RareDiseaseExitQuestionnaire.fromJsonDict(jsonDict=old_json)
        self.assertIsInstance(new_instance, self.new_model.RareDiseaseExitQuestionnaire)
        self._validate(new_instance)

    def test_migrate_reported_variants(self):

        old_ig = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_400, fill_nullables=True
        ).create()
        self._validate(old_ig)

        reported_variants_5 = MigrateReports400To500().convert_collection(
            old_ig.reportedVariants, MigrateReports400To500()._migrate_reported_variant, assembly="GRCh37"
        )

        old_hgnc_symbols = [re.genomicFeature.hgnc for rv in old_ig.reportedVariants for re in rv.reportEvents]
        new_hgnc_symbols = [ge.geneSymbol for rv in reported_variants_5 for re in rv.reportEvents for ge in re.genomicEntities]
        [self.assertIsNotNone(symbol) for symbol in old_hgnc_symbols]
        [self.assertIsNotNone(symbol) for symbol in new_hgnc_symbols]
        self.assertEqual(old_hgnc_symbols, new_hgnc_symbols)

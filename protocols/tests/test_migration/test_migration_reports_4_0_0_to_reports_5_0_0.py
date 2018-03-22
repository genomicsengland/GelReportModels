from protocols.tests.test_migration.base_test_migration import TestCaseMigration
import factory.fuzzy
from protocols import reports_4_0_0
from protocols import reports_5_0_0
from protocols.migration.migration_reports_4_0_0_to_reports_5_0_0 import MigrateReports400To500
from protocols.util.dependency_manager import VERSION_400
from protocols.util.dependency_manager import VERSION_500
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
        self.assertTrue(cr_c_400.validate(cr_c_400.toJsonDict()))
        self._check_non_empty_fields(cr_c_400)

        assembly = 'grch38'
        participant_id = "no_one"
        sample_id = 'some'
        migrated_cir_500 = MigrateReports400To500().migrate_cancer_clinical_report(
            cr_c_400, assembly=assembly, participant_id=participant_id, sample_id=sample_id
        )
        self.assertTrue(migrated_cir_500.validate(migrated_cir_500.toJsonDict()))
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
        self.assertTrue(cr_c_400.validate(cr_c_400.toJsonDict()))

        assembly = 'hg19'
        participant_id = "no_one"
        sample_id = 'some'
        migrated_cir_500 = MigrateReports400To500().migrate_cancer_clinical_report(
            cr_c_400, assembly=assembly, participant_id=participant_id, sample_id=sample_id
        )
        self.assertTrue(migrated_cir_500.validate(migrated_cir_500.toJsonDict()))

        self.assertTrue(cr_c_400.candidateVariants is None)
        self.assertTrue(migrated_cir_500.variants is None)

    def test_migrate_cancer_interpreted_genome(self):

        # creates a random clinical report cancer for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.CancerInterpretedGenome, VERSION_400, fill_nullables=True
        ).create()
        self.assertTrue(old_instance.validate(old_instance.toJsonDict()))
        self._check_non_empty_fields(old_instance)

        assembly = 'grch38'
        participant_id = "no_one"
        sample_id = 'some'
        interpretation_request_version = 1
        interpretation_service = 'testing'
        new_instance = MigrateReports400To500().migrate_cancer_interpreted_genome(
            old_instance, assembly=assembly, participant_id=participant_id, sample_id=sample_id,
            interpretation_request_version=interpretation_request_version,
            interpretation_service=interpretation_service
        )
        self.assertTrue(new_instance.validate(new_instance.toJsonDict()))
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
        self.assertTrue(old_instance.validate(old_instance.toJsonDict()))

        assembly = 'hg19'
        participant_id = "no_one"
        sample_id = 'some'
        interpretation_request_version = 1
        interpretation_service = 'testing'
        new_instance = MigrateReports400To500().migrate_cancer_interpreted_genome(
            old_instance, assembly=assembly, participant_id=participant_id, sample_id=sample_id,
            interpretation_request_version=interpretation_request_version,
            interpretation_service=interpretation_service
        )
        self.assertTrue(new_instance.validate(new_instance.toJsonDict()))
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
        old_instance.cancerParticipant.tumourSamples = [old_instance.cancerParticipant.tumourSamples[0]]
        self.assertTrue(old_instance.validate(old_instance.toJsonDict()))
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
        self.assertTrue(new_instance.validate(new_instance.toJsonDict()))
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
        old_instance.cancerParticipant.tumourSamples = [old_instance.cancerParticipant.tumourSamples[0]]
        self.assertTrue(old_instance.validate(old_instance.toJsonDict()))

        assembly = 'grCH37'
        interpretation_service = 'testing'
        new_instance = MigrateReports400To500().migrate_cancer_interpretation_request_to_cancer_interpreted_genome(
            old_instance, assembly=assembly,
            interpretation_service=interpretation_service,
            reference_database_versions={},
            software_versions={}
        )
        self.assertTrue(new_instance.validate(new_instance.toJsonDict()))
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
        self.assertTrue(old_instance.validate(old_instance.toJsonDict()))
        self._check_non_empty_fields(old_instance)

        assembly = 'grch38'
        new_instance = MigrateReports400To500().migrate_clinical_report_rd(
            old_instance, assembly=assembly
        )
        self.assertTrue(new_instance.validate(new_instance.toJsonDict()))
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
        self.assertTrue(cr_c_400.validate(cr_c_400.toJsonDict()))

        assembly = 'hg19'
        new_instance = MigrateReports400To500().migrate_clinical_report_rd(
            cr_c_400, assembly=assembly
        )
        self.assertTrue(new_instance.validate(new_instance.toJsonDict()))

        self.assertTrue(cr_c_400.candidateVariants is None)
        self.assertTrue(new_instance.variants is None)

    def test_migrate_rd_interpreted_genome(self):

        # creates a random clinical report cancer for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_400, fill_nullables=True
        ).create()  # we need to enforce that it can be cast to int
        self.assertTrue(old_instance.validate(old_instance.toJsonDict()))
        self._check_non_empty_fields(old_instance)

        assembly = 'grch38'
        new_instance = MigrateReports400To500().migrate_interpreted_genome_rd(
            old_instance, assembly=assembly, interpretation_request_version=1
        )
        self.assertTrue(new_instance.validate(new_instance.toJsonDict()))
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

        # creates a random clinical report cancer for testing not filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_400, fill_nullables=False
        ).create()
        self.assertTrue(old_instance.validate(old_instance.toJsonDict()))

        assembly = 'hg19'
        new_instance = MigrateReports400To500().migrate_interpreted_genome_rd(
            old_instance, assembly=assembly, interpretation_request_version=1
        )
        self.assertTrue(new_instance.validate(new_instance.toJsonDict()))

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
        self.assertTrue(old_instance.validate(old_instance.toJsonDict()))
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
        self.assertTrue(new_instance.validate(new_instance.toJsonDict()))
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

        # creates a random clinical report cancer for testing not filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretationRequestRD, VERSION_400, fill_nullables=False
        ).create()
        self.assertTrue(old_instance.validate(old_instance.toJsonDict()))

        assembly = 'hg19'
        new_instance = MigrateReports400To500().migrate_interpretation_request_rd_to_interpreted_genome_rd(
            old_instance, assembly=assembly, interpretation_service=interpretation_service,
            reference_database_versions={'dbSnp': 'rs12345'},
            software_versions={'intogen': '1.5'},
            report_url="blablabla.blah",
            comments=["bla", "bla!", "bla?"]
        )
        self.assertTrue(new_instance.validate(new_instance.toJsonDict()))

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
        old_instance.cancerParticipant.LDPCode = "needs to be filled"
        self._validate(old_instance)
        migrated_instance = MigrateReports400To500().migrate_cancer_interpretation_request(
            old_instance=old_instance, assembly='GRCh38'
        )
        self._validate(migrated_instance)

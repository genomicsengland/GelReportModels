import factory.fuzzy
from random import uniform

from protocols import (
    reports_2_1_0,
    reports_3_0_0,
    reports_4_0_0,
    reports_5_0_0,
    reports_6_0_0,
    participant_1_0_0,
    participant_1_0_3,
)
from protocols.util.dependency_manager import (
    VERSION_210,
    VERSION_300,
    VERSION_400,
    VERSION_500,
    VERSION_61,
    VERSION_70)
from protocols.migration.base_migration import MigrationError
from protocols.util.factories.avro_factory import FactoryAvro
from protocols.migration.migration_helpers import MigrationHelpers
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.tests.test_migration.base_test_migration import TestCaseMigration


class ActionFactory600(FactoryAvro):
    class Meta:
        model = reports_6_0_0.Actions
    _version = VERSION_70
    actionType = factory.fuzzy.FuzzyChoice(['therapy', 'therapeutic', 'prognosis', 'diagnosis'])
    status = factory.fuzzy.FuzzyChoice(['clinical', 'pre-clinical'])
    evidence = ["this", "that"]
    drug = factory.fuzzy.FuzzyText()
    variantActionable = factory.fuzzy.FuzzyChoice([True, False])
    comments = ["this", "that"]
    url = factory.fuzzy.FuzzyText()
    evidenceType = factory.fuzzy.FuzzyText()
    source = factory.fuzzy.FuzzyText()


class ActionFactory400(FactoryAvro):
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


class ActionFactory300(FactoryAvro):
    class Meta:
        model = reports_3_0_0.Actions

    _version = VERSION_300

    actionType = factory.fuzzy.FuzzyChoice(['therapy', 'therapeutic', 'prognosis', 'diagnosis'])
    status = factory.fuzzy.FuzzyChoice(['clinical', 'pre-clinical'])
    evidence = ["this", "that"]
    drug = factory.fuzzy.FuzzyText()
    variantActionable = factory.fuzzy.FuzzyChoice([True, False])
    comments = ["this", "that"]
    url = factory.fuzzy.FuzzyText()
    evidenceType = factory.fuzzy.FuzzyText()
    source = factory.fuzzy.FuzzyText()


class FileFactory300(FactoryAvro):
    class Meta:
        model = reports_3_0_0.File

    _version = VERSION_300

    SampleId = factory.fuzzy.FuzzyText()
    URIFile = factory.fuzzy.FuzzyText()
    fileType = factory.fuzzy.FuzzyChoice([reports_3_0_0.FileType.BAM, reports_3_0_0.FileType.BigWig,
                                          reports_3_0_0.FileType.ANN, reports_3_0_0.FileType.VCF_small])
    md5Sum = None


class FileFactory210(FactoryAvro):
    class Meta:
        model = reports_2_1_0.File

    _version = VERSION_210

    SampleId = factory.fuzzy.FuzzyText()
    URIFile = factory.fuzzy.FuzzyText()
    fileType = factory.fuzzy.FuzzyChoice([reports_3_0_0.FileType.BAM, reports_3_0_0.FileType.BigWig,
                                          reports_3_0_0.FileType.ANN, reports_3_0_0.FileType.VCF_small])


class TestMigrationHelpers(TestCaseMigration):

    def setUp(self):
        GenericFactoryAvro.register_factory(
            reports_4_0_0.Actions, ActionFactory400, VERSION_400, fill_nullables=True)
        GenericFactoryAvro.register_factory(
            reports_3_0_0.Actions, ActionFactory300, VERSION_300, fill_nullables=True)
        GenericFactoryAvro.register_factory(
            reports_3_0_0.File, FileFactory300, VERSION_300, fill_nullables=True)
        GenericFactoryAvro.register_factory(
            reports_2_1_0.File, FileFactory210, VERSION_210, fill_nullables=True)
        GenericFactoryAvro.register_factory(
            reports_4_0_0.Actions, ActionFactory400, VERSION_400, fill_nullables=False)
        GenericFactoryAvro.register_factory(
            reports_3_0_0.Actions, ActionFactory300, VERSION_300, fill_nullables=False)
        GenericFactoryAvro.register_factory(
            reports_3_0_0.File, FileFactory300, VERSION_300, fill_nullables=False)
        GenericFactoryAvro.register_factory(
            reports_2_1_0.File, FileFactory210, VERSION_210, fill_nullables=False)

    def test_migrate_interpretation_request_rd_400_600(self, fill_nullables=True):

        # tests IR RD 400 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_4_0_0.InterpretationRequestRD, VERSION_400, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        self.assertIsInstance(old_instance, reports_4_0_0.InterpretationRequestRD)

        migrated_instance = MigrationHelpers.migrate_interpretation_request_rd_to_latest(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.InterpretationRequestRD)
        self._validate(migrated_instance)
        self.assertEqual(migrated_instance.versionControl.gitVersionControl, '6.0.0')

    def test_migrate_interpretation_request_rd_400_600_no_nullables(self):
        self.test_migrate_interpretation_request_rd_400_600(fill_nullables=False)

    def test_migrate_interpretation_request_rd_600_300(self, fill_nullables=True):
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_6_0_0.InterpretationRequestRD, VERSION_70, fill_nullables=fill_nullables
        ).create()
        # there is an explicit check for pedigree even though it's nullable.
        old_instance.pedigree = GenericFactoryAvro.get_factory_avro(
            reports_6_0_0.Pedigree, VERSION_70, fill_nullables=fill_nullables
        ).create()
        old_ig = GenericFactoryAvro.get_factory_avro(
            reports_6_0_0.InterpretedGenome, VERSION_70, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        self.assertIsInstance(old_instance, reports_6_0_0.InterpretationRequestRD)

        migrated_instance = MigrationHelpers.reverse_migrate_interpretation_request_rd_to_v3(old_instance.toJsonDict(), old_ig.toJsonDict())
        self.assertIsInstance(migrated_instance, reports_3_0_0.InterpretationRequestRD)
        self._validate(migrated_instance)
        self.assertEqual(migrated_instance.versionControl.GitVersionControl, '3.0.0')

    def test_migrate_interpretation_request_rd_600_300_no_nullables(self):
        self.test_migrate_interpretation_request_rd_600_300(fill_nullables=False)

    def test_migrate_interpretation_request_rd_300_600(self, fill_nullables=True):

        # tests IR RD 300 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_3_0_0.InterpretationRequestRD, VERSION_300, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        self.assertIsInstance(old_instance, reports_3_0_0.InterpretationRequestRD)

        migrated_instance = MigrationHelpers.migrate_interpretation_request_rd_to_latest(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.InterpretationRequestRD)
        self._validate(migrated_instance)
        self.assertEqual(migrated_instance.versionControl.gitVersionControl, '6.0.0')

    def test_migrate_interpretation_request_rd_300_600_no_nullables(self):
        self.test_migrate_interpretation_request_rd_300_600(fill_nullables=False)

    def test_migrate_interpretation_request_rd_210_600(self, fill_nullables=True):

        # tests IR RD 210 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_2_1_0.InterpretationRequestRD, VERSION_210, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        self.assertIsInstance(old_instance, reports_2_1_0.InterpretationRequestRD)

        migrated_instance = MigrationHelpers.migrate_interpretation_request_rd_to_latest(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.InterpretationRequestRD)
        self._validate(migrated_instance)
        self.assertEqual(migrated_instance.versionControl.gitVersionControl, '6.0.0')

    def test_migrate_interpretation_request_rd_210_600_no_nullables(self):
        self.test_migrate_interpretation_request_rd_210_600(fill_nullables=False)

    def test_migrate_interpretation_request_rd_500_600(self, fill_nullables=True):

        # tests IR RD 500 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_5_0_0.InterpretationRequestRD, VERSION_61, fill_nullables=fill_nullables
        ).create()
        self.assertIsInstance(old_instance, reports_5_0_0.InterpretationRequestRD)
        self._validate(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpretation_request_rd_to_latest(
            json_dict=old_instance.toJsonDict()
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.InterpretationRequestRD)
        self._validate(migrated_instance)
        self.assertEqual(migrated_instance.versionControl.gitVersionControl, '6.0.0')

    def test_migrate_interpretation_request_rd_500_600_no_nullables(self):
        self.test_migrate_interpretation_request_rd_500_600(fill_nullables=False)

    def test_migrate_interpretation_request_rd_to_interpreted_genome_400_600(self, fill_nullables=True):

        # tests IR 400 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_4_0_0.InterpretationRequestRD, VERSION_400, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpretation_request_rd_to_interpreted_genome_latest(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.InterpretedGenome)
        self._validate(migrated_instance)

    def test_migrate_interpretation_request_rd_to_interpreted_genome_400_600_nulls(self):
        self.test_migrate_interpretation_request_rd_to_interpreted_genome_400_600(fill_nullables=False)

    def test_migrate_interpretation_request_rd_to_interpreted_genome_300_600(self, fill_nullables=True):

        # tests IR 300 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_3_0_0.InterpretationRequestRD, VERSION_300, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpretation_request_rd_to_interpreted_genome_latest(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.InterpretedGenome)
        self._validate(migrated_instance)

    def test_migrate_interpretation_request_rd_to_interpreted_genome_300_600_null(self):
        self.test_migrate_interpretation_request_rd_to_interpreted_genome_300_600(fill_nullables=False)

    def test_migrate_interpretation_request_rd_to_interpreted_genome_210_600(self, fill_nullables=True):

        # tests IR 210 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_2_1_0.InterpretationRequestRD, VERSION_210, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpretation_request_rd_to_interpreted_genome_latest(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.InterpretedGenome)
        self._validate(migrated_instance)

    def test_migrate_interpretation_request_rd_to_interpreted_genome_210_600_nulls(self):
        self.test_migrate_interpretation_request_rd_to_interpreted_genome_210_600(fill_nullables=False)

    def test_migrate_interpreted_genome_rd_400_600(self, fill_nullables=True):

        # tests IG 400 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_4_0_0.InterpretedGenomeRD, VERSION_400, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpreted_genome_rd_to_latest(
            old_instance.toJsonDict(), assembly='GRCh38', interpretation_request_version=1
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.InterpretedGenome)
        self._validate(migrated_instance)

    def test_migrate_interpreted_genome_rd_400_600_nulls(self):
        self.test_migrate_interpreted_genome_rd_400_600(fill_nullables=False)

    def test_migrate_interpreted_genome_rd_600_300(self, fill_nullables=True):

        # tests IG 400 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_6_0_0.InterpretedGenome, VERSION_70, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.reverse_migrate_interpreted_genome_rd_to_v3(old_instance.toJsonDict())
        self.assertIsInstance(migrated_instance, reports_3_0_0.InterpretedGenomeRD)
        self._validate(migrated_instance)

    def test_migrate_interpreted_genome_rd_600_300_nulls(self):
        self.test_migrate_interpreted_genome_rd_600_300(fill_nullables=False)

    def test_migrate_interpreted_genome_rd_300_600(self, fill_nullables=True):

        # tests IG 300 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_3_0_0.InterpretedGenomeRD, VERSION_300, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpreted_genome_rd_to_latest(
            old_instance.toJsonDict(), assembly='GRCh38', interpretation_request_version=1
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.InterpretedGenome)
        self._validate(migrated_instance)

    def test_migrate_interpreted_genome_rd_300_600_nulls(self):
        self.test_migrate_interpreted_genome_rd_300_600(fill_nullables=False)

    def test_migrate_interpreted_genome_rd_210_600(self, fill_nullables=True):

        # tests IG 210 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_2_1_0.InterpretedGenomeRD, VERSION_210, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpreted_genome_rd_to_latest(
            old_instance.toJsonDict(), assembly='GRCh38', interpretation_request_version=1
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.InterpretedGenome)
        self._validate(migrated_instance)

    def test_migrate_interpreted_genome_rd_210_600_nulls(self):
        self.test_migrate_interpreted_genome_rd_210_600(fill_nullables=False)

    def test_migrate_interpreted_genome_rd_500_600(self, fill_nullables=True):

        # tests IG 500 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_5_0_0.InterpretedGenomeRD, VERSION_61, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpreted_genome_rd_to_latest(
            old_instance.toJsonDict()
        )
        self._validate(migrated_instance)

    def test_migrate_interpreted_genome_rd_500_600_nulls(self):
        self.test_migrate_interpreted_genome_rd_500_600(fill_nullables=True)

    def test_migrate_rd_clinical_report_400_600(self, fill_nullables=True):

        # tests IG 400 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_4_0_0.ClinicalReportRD, VERSION_400, fill_nullables=fill_nullables
        ).create()
        old_instance.interpretationRequestVersion = str(factory.fuzzy.FuzzyInteger(0).fuzz())
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        migrated_instance = MigrationHelpers.migrate_clinical_report_rd_to_latest(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.ClinicalReport)
        self._validate(migrated_instance)

    def test_migrate_rd_clinical_report_400_600_nulls(self):
        self.test_migrate_rd_clinical_report_400_600(fill_nullables=False)

    def test_migrate_rd_clinical_report_300_600(self, fill_nullables=True):

        # tests IG 300 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_3_0_0.ClinicalReportRD, VERSION_300, fill_nullables=fill_nullables
        ).create()
        old_instance.interpretationRequestVersion = str(factory.fuzzy.FuzzyInteger(0).fuzz())
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_clinical_report_rd_to_latest(
            old_instance.toJsonDict(), assembly='GRCh38')
        self.assertIsInstance(migrated_instance, reports_6_0_0.ClinicalReport)
        self._validate(migrated_instance)

    def test_migrate_rd_clinical_report_300_600_nulls(self):
        self.test_migrate_rd_clinical_report_300_600(fill_nullables=False)

    def test_migrate_rd_clinical_report_600_300(self, fill_nullables=True):
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_6_0_0.ClinicalReport, VERSION_70, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.reverse_migrate_clinical_report_rd_to_v3(old_instance.toJsonDict())
        self.assertIsInstance(migrated_instance, reports_3_0_0.ClinicalReportRD)
        self._validate(migrated_instance)

    def test_migrate_rd_clinical_report_600_300_nulls(self):
        self.test_migrate_rd_clinical_report_600_300(fill_nullables=False)

    def test_migrate_rd_clinical_report_210_600(self, fill_nullables=True):

        # tests IG 210 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_2_1_0.ClinicalReportRD, VERSION_210, fill_nullables=fill_nullables
        ).create()
        old_instance.interpretationRequestVersion = str(factory.fuzzy.FuzzyInteger(0).fuzz())
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_clinical_report_rd_to_latest(
            old_instance.toJsonDict(), assembly='GRCh38')
        self.assertIsInstance(migrated_instance, reports_6_0_0.ClinicalReport)
        self._validate(migrated_instance)

    def test_migrate_rd_clinical_report_210_600_nulls(self):
        self.test_migrate_rd_clinical_report_210_600(fill_nullables=False)

    def test_migrate_rd_clinical_report_500_600(self, fill_nullables=True):

        # tests IG 500 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_5_0_0.ClinicalReportRD, VERSION_61, fill_nullables=fill_nullables
        ).create()

        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
            # Create a float_list of 5 floats and after casting to string assign to the fdp50 values of the old instance
            # IF THE fdp50 VALUE HAS MORE THAN 11 DECIMAL PLACES THEN THE CONVERSION TO FLOAT WILL FAIL
            float_list = [round(uniform(1.0, 10.0), 11) for _ in range(5)]

            for index_value, variant in enumerate(old_instance.variants):
                variant.variantAttributes.fdp50 = str(float_list[index_value])

        migrated_instance = MigrationHelpers.migrate_clinical_report_rd_to_latest(old_instance.toJsonDict())
        self.assertIsInstance(migrated_instance, reports_6_0_0.ClinicalReport)
        self._validate(migrated_instance)

        if fill_nullables:
            # Check that the fdp50 values have been correctly converted from string to float
            for index_value, variant in enumerate(migrated_instance.variants):
                self.assertEqual(variant.variantAttributes.fdp50, float_list[index_value])

    def test_migrate_rd_clinical_report_500_600_nulls(self):
        self.test_migrate_rd_clinical_report_500_600(fill_nullables=False)

    def test_migrate_pedigree_300_110(self, fill_nullables=True):
        # tests reports 300 -> participants 103
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_3_0_0.Pedigree, VERSION_300, fill_nullables=fill_nullables
        ).create()
        for participant in old_instance.participants:
            for disorder in participant.disorderList:
                disorder.ageOfOnset = str(factory.fuzzy.FuzzyFloat(0.0).fuzz())
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        migrated_instance = MigrationHelpers.migrate_pedigree_to_latest(old_instance.toJsonDict())
        self._validate(migrated_instance)

    def test_migrate_pedigree_300_110_nulls(self):
        self.test_migrate_pedigree_300_110(fill_nullables=False)

    def test_migrate_pedigree_100_110(self, fill_nullables=True):
        # tests IG participants 100 -> participants 103
        old_instance = GenericFactoryAvro.get_factory_avro(
            participant_1_0_0.Pedigree, VERSION_400, fill_nullables=fill_nullables
        ).create()
        for member in old_instance.members:
            if member.disorderList:
                for disorder in member.disorderList:
                    disorder.ageOfOnset = str(factory.fuzzy.FuzzyFloat(0.0).fuzz())
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        migrated_instance = MigrationHelpers.migrate_pedigree_to_latest(old_instance.toJsonDict())
        self._validate(migrated_instance)

    def test_migrate_pedigree_100_110_nulls(self):
        self.test_migrate_pedigree_100_110(fill_nullables=False)

    def test_migrate_pedigree_103_110(self, fill_nullables=True):

        # tests pedigree participants 103 -> participants 103
        old_instance = GenericFactoryAvro.get_factory_avro(
            participant_1_0_3.Pedigree, VERSION_500, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        migrated_instance = MigrationHelpers.migrate_pedigree_to_latest(old_instance.toJsonDict())
        self._validate(migrated_instance)

    def test_migrate_pedigree_103_110_nulls(self):
        self.test_migrate_pedigree_103_110(fill_nullables=False)

    def test_migrate_pedigree_110_110(self, fill_nullables=True):
        # tests pedigree participants 103 -> participants 103
        old_instance = GenericFactoryAvro.get_factory_avro(
            participant_1_0_3.Pedigree, VERSION_61, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        migrated_instance = MigrationHelpers.migrate_pedigree_to_latest(old_instance.toJsonDict())
        self._validate(migrated_instance)

    def test_migrate_pedigree_110_110_nulls(self):
        self.test_migrate_pedigree_110_110(fill_nullables=False)

    def test_migrate_interpretation_request_cancer_400_600(self, fill_nullables=True):

        # tests CIR 400 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_4_0_0.CancerInterpretationRequest, VERSION_400, fill_nullables=fill_nullables
        ).create()
        if not fill_nullables:
            old_instance.cancerParticipant.LDPCode = "12345"
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpretation_request_cancer_to_latest(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.CancerInterpretationRequest)
        self._validate(migrated_instance)
        self.assertEqual(migrated_instance.versionControl.gitVersionControl, '6.0.0')

    def test_migrate_interpretation_request_cancer_400_600_nulls(self):
        self.test_migrate_interpretation_request_cancer_400_600(fill_nullables=False)

    def test_migrate_interpretation_request_cancer_600_400(self, fill_nullables=True):
        old_instance = self.get_valid_object(
            reports_6_0_0.CancerInterpretationRequest, VERSION_70, fill_nullables=fill_nullables
        )
        old_ig = self.get_valid_object(
            reports_6_0_0.InterpretedGenome, VERSION_70, fill_nullables=fill_nullables
        )
        small_variant = self.get_valid_object(reports_6_0_0.SmallVariant, VERSION_70, fill_nullables=fill_nullables)
        old_ig.variants = [small_variant]
        migrated_instance = MigrationHelpers.reverse_migrate_interpretation_request_cancer_to_v4(
            old_instance.toJsonDict(), old_ig.toJsonDict()
        )
        self.assertIsInstance(migrated_instance, reports_4_0_0.CancerInterpretationRequest)
        self._validate(migrated_instance)
        self.assertEqual(migrated_instance.versionControl.gitVersionControl, '4.0.0')

    def test_migrate_interpretation_request_cancer_600_400_nulls(self):
        self.test_migrate_interpretation_request_cancer_600_400(fill_nullables=False)

    def test_migrate_interpretation_request_cancer_300_600(self, fill_nullables=True):

        # tests CIR 300 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_3_0_0.CancerInterpretationRequest, VERSION_300, fill_nullables=fill_nullables
        ).create()
        for cancer_sample in old_instance.cancerParticipant.cancerSamples:
            cancer_sample.labId = "12345"
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance, exclusions=["md5Sum"])

        migrated_instance = MigrationHelpers.migrate_interpretation_request_cancer_to_latest(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.CancerInterpretationRequest)
        self._validate(migrated_instance)
        self.assertEqual(migrated_instance.versionControl.gitVersionControl, '6.0.0')

    def test_migrate_interpretation_request_cancer_300_600_nulls(self):
        self.test_migrate_interpretation_request_cancer_300_600(fill_nullables=False)

    def test_migrate_interpretation_request_cancer_500_600(self, fill_nullables=True):

        # tests CIR 500 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_5_0_0.CancerInterpretationRequest, VERSION_61, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpretation_request_cancer_to_latest(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.CancerInterpretationRequest)
        self._validate(migrated_instance)
        self.assertEqual(migrated_instance.versionControl.gitVersionControl, '6.0.0')

    def test_migrate_interpretation_request_cancer_500_600_nulls(self):
        self.test_migrate_interpretation_request_cancer_500_600(fill_nullables=False)

    def test_migrate_interpretation_request_cancer_to_interpreted_genome_400_500(self, fill_nullables=True):

        # tests IR 400 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_4_0_0.CancerInterpretationRequest, VERSION_400, fill_nullables=fill_nullables
        ).create()
        if not fill_nullables:
            old_instance.cancerParticipant.LDPCode = "12345"
        # only one tumour sample
        old_instance.cancerParticipant.tumourSamples = old_instance.cancerParticipant.tumourSamples[0:1]
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpretation_request_cancer_to_interpreted_genome_latest(
            old_instance.toJsonDict(), assembly='GRCh38', interpretation_service='testing',
            reference_database_versions={'thisdb': 'thatversion'}, software_versions={'testing': '1.2'},
            report_url='fake.url', comments=['blah', 'blah!', 'blah?'])
        self._validate(migrated_instance)

    def test_migrate_interpretation_request_cancer_to_interpreted_genome_400_500_nulls(self):
        self.test_migrate_interpretation_request_cancer_to_interpreted_genome_400_500(fill_nullables=False)

    def test_migrate_interpretation_request_cancer_to_interpreted_genome_300_500(self, fill_nullables=True):

        # tests IR 300 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_3_0_0.CancerInterpretationRequest, VERSION_300, fill_nullables=fill_nullables
        ).create()
        # only one tumour sample
        old_instance.cancerParticipant.cancerSamples = old_instance.cancerParticipant.cancerSamples[0:2]
        old_instance.cancerParticipant.cancerSamples[0].labId = "12345"
        old_instance.cancerParticipant.cancerSamples[0].sampleType = reports_3_0_0.SampleType.tumor
        old_instance.cancerParticipant.cancerSamples[1].labId = "12345"
        old_instance.cancerParticipant.cancerSamples[1].sampleType = reports_3_0_0.SampleType.germline
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance, exclusions=["md5Sum"])

        migrated_instance = MigrationHelpers.migrate_interpretation_request_cancer_to_interpreted_genome_latest(
            old_instance.toJsonDict(), assembly='GRCh38', interpretation_service='testing',
            reference_database_versions={'thisdb': 'thatversion'}, software_versions={'testing': '1.2'},
            report_url='fake.url', comments=['blah', 'blah!', 'blah?']
        )
        self._validate(migrated_instance)

    def test_migrate_interpretation_request_cancer_to_interpreted_genome_300_500_nulls(self):
        self.test_migrate_interpretation_request_cancer_to_interpreted_genome_300_500(fill_nullables=False)

    def test_migrate_interpretation_request_cancer_to_interpreted_genome_500_500(self, fill_nullables=True):

        # tests IG 500 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_5_0_0.CancerInterpretationRequest, VERSION_61, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        with self.assertRaises(MigrationError):
            MigrationHelpers.migrate_interpretation_request_cancer_to_interpreted_genome_latest(
                old_instance.toJsonDict(), assembly='GRCh38', interpretation_service='testing',
                reference_database_versions={'thisdb': 'thatversion'}, software_versions={'testing': '1.2'},
                report_url='fake.url', comments=['blah', 'blah!', 'blah?'])
            self.assertTrue(False)

    def test_migrate_interpretation_request_cancer_to_interpreted_genome_500_500_nulls(self):
        self.test_migrate_interpretation_request_cancer_to_interpreted_genome_500_500(fill_nullables=False)

    def test_migrate_interpreted_genome_cancer_400_500(self, fill_nullables=True):

        # tests IR 400 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_4_0_0.CancerInterpretedGenome, VERSION_400, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers().migrate_interpreted_genome_cancer_to_latest(
            old_instance.toJsonDict(), assembly='GRCh38', participant_id='123', sample_id='456',
            interpretation_request_version=5, interpretation_service='congenica')
        self._validate(migrated_instance)

    def test_migrate_interpreted_genome_cancer_400_500_nulls(self):
        self.test_migrate_interpreted_genome_cancer_400_500(fill_nullables=False)

    def test_migrate_interpreted_genome_cancer_300_500(self, fill_nullables=True):

        # tests IR 300 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_3_0_0.CancerInterpretedGenome, VERSION_300, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance, exclusions=["md5Sum"])

        with self.assertRaises(MigrationError):
            MigrationHelpers().migrate_interpreted_genome_cancer_to_latest(
                old_instance.toJsonDict(), assembly='GRCh38', participant_id='123', sample_id='456',
                interpretation_request_version=5, interpretation_service='congenica')
            self.assertTrue(False)

    def test_migrate_interpreted_genome_cancer_300_500_nulls(self):
        self.test_migrate_interpreted_genome_cancer_300_500(fill_nullables=False)

    def test_migrate_interpreted_genome_cancer_500_600(self, fill_nullables=True):

        # tests C IG 500 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_5_0_0.CancerInterpretedGenome, VERSION_61, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers().migrate_interpreted_genome_cancer_to_latest(
            old_instance.toJsonDict()
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.InterpretedGenome)
        self._validate(migrated_instance)

    def test_migrate_interpreted_genome_cancer_500_600_nulls(self):
        self.test_migrate_interpreted_genome_cancer_500_600(fill_nullables=False)


    def test_migrate_interpreted_genome_cancer_600_400(self, fill_nullables=True):
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_6_0_0.InterpretedGenome, VERSION_70, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers().reverse_migrate_interpreted_genome_cancer_to_v4(
            old_instance.toJsonDict()
        )
        self.assertIsInstance(migrated_instance, reports_4_0_0.CancerInterpretedGenome)
        self._validate(migrated_instance)

    def test_migrate_interpreted_genome_cancer_500_600_nulls(self):
        self.test_migrate_interpreted_genome_cancer_500_600(fill_nullables=False)

    def test_migrate_clinical_report_cancer_400_600(self, fill_nullables=True):

        # tests IR 400 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_4_0_0.ClinicalReportCancer, VERSION_400, fill_nullables=fill_nullables
        ).create()
        old_instance.interpretationRequestVersion = '789'
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_clinical_report_cancer_to_latest(
            old_instance.toJsonDict(), sample_id='123', assembly='GRCh38', participant_id='456'
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.ClinicalReport)
        self._validate(migrated_instance)

    def test_migrate_clinical_report_cancer_400_600_nulls(self):
        self.test_migrate_clinical_report_cancer_400_600(fill_nullables=False)

    def test_migrate_clinical_report_cancer_300_600(self, fill_nullables=True):

        # tests IR 300 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_3_0_0.ClinicalReportCancer, VERSION_300, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance, exclusions=["md5Sum"])

        with self.assertRaises(MigrationError):
            MigrationHelpers.migrate_clinical_report_cancer_to_latest(
                json_dict=old_instance.toJsonDict(), sample_id='123', assembly='GRCh38', participant_id='456'
            )

    def test_migrate_clinical_report_cancer_300_600_nulls(self):
        self.test_migrate_clinical_report_cancer_300_600(fill_nullables=False)

    def test_migrate_clinical_report_cancer_500_600(self, fill_nullables=True):

        # tests IG 500 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_5_0_0.ClinicalReportCancer, VERSION_61, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_clinical_report_cancer_to_latest(
            json_dict=old_instance.toJsonDict(),
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.ClinicalReport)
        self._validate(migrated_instance)

    def test_migrate_clinical_report_cancer_500_600_nulls(self):
        self.test_migrate_clinical_report_cancer_500_600(fill_nullables=False)

    def test_migrate_questionnaire_rd_300_600(self, fill_nullables=True):

        # tests EQ 300 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_3_0_0.RareDiseaseExitQuestionnaire, VERSION_300, fill_nullables=fill_nullables
        ).create()
        old_instance = self.populate_exit_questionnaire_variant_details(eq=old_instance)
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_exit_questionnaire_rd_to_latest(
            json_dict=old_instance.toJsonDict(), assembly="GRCh38"
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.RareDiseaseExitQuestionnaire)
        self._validate(migrated_instance)

    def test_migrate_questionnaire_rd_300_600_nulls(self):
        self.test_migrate_questionnaire_rd_300_600(fill_nullables=False)

    def test_migrate_questionnaire_rd_600_300(self, fill_nullables=True):

        # tests EQ 300 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_6_0_0.RareDiseaseExitQuestionnaire, VERSION_70, fill_nullables=fill_nullables
        ).create()
        old_instance = self.populate_exit_questionnaire_variant_details(eq=old_instance)
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.reverse_migrate_exit_questionnaire_rd_to_v3(
            json_dict=old_instance.toJsonDict()
        )
        self.assertIsInstance(migrated_instance, reports_3_0_0.RareDiseaseExitQuestionnaire)
        self._validate(migrated_instance)

    def test_migrate_questionnaire_rd_600_300_nulls(self):
        self.test_migrate_questionnaire_rd_600_300(fill_nullables=False)

    def test_migrate_questionnaire_rd_400_600(self, fill_nullables=True):

        # tests EQ 400 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_4_0_0.RareDiseaseExitQuestionnaire, VERSION_400, fill_nullables=fill_nullables
        ).create()
        old_instance = self.populate_exit_questionnaire_variant_details(eq=old_instance)
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_exit_questionnaire_rd_to_latest(
            json_dict=old_instance.toJsonDict(), assembly="GRCh38"
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.RareDiseaseExitQuestionnaire)
        self._validate(migrated_instance)

    def test_migrate_questionnaire_rd_400_600_nulls(self):
        self.test_migrate_questionnaire_rd_400_600(fill_nullables=False)

    def test_migrate_questionnaire_rd_500_600(self, fill_nullables=True):

        # tests EQ 500 -> 600
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_5_0_0.RareDiseaseExitQuestionnaire, VERSION_61, fill_nullables=fill_nullables
        ).create()
        old_instance = self.populate_exit_questionnaire_variant_details(eq=old_instance)
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_exit_questionnaire_rd_to_latest(
            json_dict=old_instance.toJsonDict(), assembly="GRCh38"
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.RareDiseaseExitQuestionnaire)
        self._validate(migrated_instance)

    def test_migrate_questionnaire_rd_500_600_nulls(self):
        self.test_migrate_questionnaire_rd_500_600(fill_nullables=False)

    def test_migrate_cancer_participant_100_110(self, fill_nullables=True):

        # tests IG participants 100 -> participants 103
        old_instance = GenericFactoryAvro.get_factory_avro(
            participant_1_0_0.CancerParticipant, VERSION_400, fill_nullables=fill_nullables
        ).create()  # type: participant_1_0_0.CancerParticipant
        old_instance.LDPCode = "fakedLDP"
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        migrated_instance = MigrationHelpers.migrate_cancer_participant_to_latest(old_instance.toJsonDict())
        self._validate(migrated_instance)

    def test_migrate_cancer_participant_100_110_nulls(self):
        self.test_migrate_cancer_participant_100_110(fill_nullables=False)

    def test_migrate_cancer_participant_103_110(self, fill_nullables=True):

        # tests pedigree participants 103 -> participants 103
        old_instance = GenericFactoryAvro.get_factory_avro(
            participant_1_0_3.CancerParticipant, VERSION_500, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        migrated_instance = MigrationHelpers.migrate_cancer_participant_to_latest(old_instance.toJsonDict())
        self._validate(migrated_instance)

    def test_migrate_cancer_participant_103_110_nulls(self):
        self.test_migrate_cancer_participant_103_110(fill_nullables=False)

    def test_migrate_cancer_participant_110_110(self, fill_nullables=True):

        # tests pedigree participants 103 -> participants 103
        old_instance = GenericFactoryAvro.get_factory_avro(
            participant_1_0_3.CancerParticipant, VERSION_61, fill_nullables=fill_nullables
        ).create()
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        migrated_instance = MigrationHelpers.migrate_cancer_participant_to_latest(old_instance.toJsonDict())
        self._validate(migrated_instance)

    def test_migrate_cancer_participant_110_110_nulls(self):
        self.test_migrate_cancer_participant_110_110(fill_nullables=False)

    def test_migrate_cancer_exit_questionnaire_to_latest(self, fill_nullables=True):
        # tests pedigree C EQ 5 -> C EQ 6
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_5_0_0.CancerExitQuestionnaire, VERSION_61, fill_nullables=fill_nullables
        ).create()
        old_instance = self.populate_c_eq_variant_level_questions_variant_details(old_c_eq=old_instance)
        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)
        migrated_instance = MigrationHelpers.migrate_cancer_exit_questionnaire_to_latest(
            json_dict=old_instance.toJsonDict(), assembly="GRCh38"
        )
        self.assertIsInstance(migrated_instance, reports_6_0_0.CancerExitQuestionnaire)
        self._validate(migrated_instance)

    def test_migrate_cancer_exit_questionnaire_to_latest_no_nullables(self):
        self.test_migrate_cancer_exit_questionnaire_to_latest(fill_nullables=False)

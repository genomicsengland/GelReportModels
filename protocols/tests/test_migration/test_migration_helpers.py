from protocols.tests.test_migration.base_test_migration import TestCaseMigration
import factory.fuzzy
from protocols import reports_2_1_0, reports_3_0_0, reports_4_0_0, reports_5_0_0, participant_1_0_0, participant_1_0_3
from protocols.migration.migration_reports_4_0_0_to_reports_5_0_0 import MigrateReports400To500
from protocols.util.dependency_manager import VERSION_210, VERSION_300, VERSION_400, VERSION_500, VERSION_61
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.util.factories.avro_factory import FactoryAvro

from protocols.migration.migration_helpers import MigrationHelpers


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

    def test_migrate_interpretation_request_rd_400_500(self):

        # tests IR 400 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_4_0_0.InterpretationRequestRD, VERSION_400, fill_nullables=True
        ).create()
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpretation_request_rd_to_version_5_0_0(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self._validate(migrated_instance)

    def test_migrate_interpretation_request_rd_300_500(self):

        # tests IR 300 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_3_0_0.InterpretationRequestRD, VERSION_300, fill_nullables=True
        ).create()
        self._validate(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpretation_request_rd_to_version_5_0_0(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self._validate(migrated_instance)

    def test_migrate_interpretation_request_rd_210_500(self):

        # tests IR 210 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_2_1_0.InterpretationRequestRD, VERSION_210, fill_nullables=True
        ).create()
        self._validate(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpretation_request_rd_to_version_5_0_0(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self._validate(migrated_instance)

    def test_migrate_interpretation_request_rd_500_500(self):

        # tests IG 500 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_5_0_0.InterpretedGenomeRD, VERSION_61, fill_nullables=True
        ).create()
        self._validate(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpretation_request_rd_to_version_5_0_0(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self._validate(migrated_instance)

    def test_migrate_interpreted_genome_rd_400_500(self):

        # tests IG 400 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_4_0_0.InterpretedGenomeRD, VERSION_400, fill_nullables=True
        ).create()
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpreted_genome_rd_to_version_5_0_0(
            old_instance.toJsonDict(), assembly='GRCh38', interpretation_request_version=1
        )
        self._validate(migrated_instance)

    def test_migrate_interpreted_genome_rd_300_500(self):

        # tests IG 300 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_3_0_0.InterpretedGenomeRD, VERSION_300, fill_nullables=True
        ).create()
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpreted_genome_rd_to_version_5_0_0(
            old_instance.toJsonDict(), assembly='GRCh38', interpretation_request_version=1
        )
        self._validate(migrated_instance)

    def test_migrate_interpreted_genome_rd_210_500(self):

        # tests IG 210 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_2_1_0.InterpretedGenomeRD, VERSION_210, fill_nullables=True
        ).create()
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpreted_genome_rd_to_version_5_0_0(
            old_instance.toJsonDict(), assembly='GRCh38', interpretation_request_version=1
        )
        self._validate(migrated_instance)

    def test_migrate_interpreted_genome_rd_500_500(self):

        # tests IG 500 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_5_0_0.InterpretedGenomeRD, VERSION_61, fill_nullables=True
        ).create()
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_interpreted_genome_rd_to_version_5_0_0(
            old_instance.toJsonDict(), assembly='GRCh38', interpretation_request_version=1
        )
        self._validate(migrated_instance)

    def test_migrate_rd_clinical_report_400_500(self):

        # tests IG 400 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_4_0_0.ClinicalReportRD, VERSION_400, fill_nullables=True
        ).create()
        old_instance.interpretationRequestVersion = str(factory.fuzzy.FuzzyInteger(0).fuzz())
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)
        migrated_instance = MigrationHelpers.migrate_clinical_report_rd_to_version_5_0_0(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self._validate(migrated_instance)

    def test_migrate_rd_clinical_report_300_500(self):

        # tests IG 300 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_3_0_0.ClinicalReportRD, VERSION_300, fill_nullables=True
        ).create()
        old_instance.interpretationRequestVersion = str(factory.fuzzy.FuzzyInteger(0).fuzz())
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_clinical_report_rd_to_version_5_0_0(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self._validate(migrated_instance)

    def test_migrate_rd_clinical_report_210_500(self):

        # tests IG 210 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_2_1_0.ClinicalReportRD, VERSION_210, fill_nullables=True
        ).create()
        old_instance.interpretationRequestVersion = str(factory.fuzzy.FuzzyInteger(0).fuzz())
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_clinical_report_rd_to_version_5_0_0(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self._validate(migrated_instance)

    def test_migrate_rd_clinical_report_500_500(self):

        # tests IG 500 -> 500
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_5_0_0.ClinicalReportRD, VERSION_61, fill_nullables=True
        ).create()
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_clinical_report_rd_to_version_5_0_0(
            old_instance.toJsonDict(), assembly='GRCh38'
        )
        self._validate(migrated_instance)

    def test_migrate_pedigree_300_103(self):

        # tests reports 300 -> participants 103
        old_instance = GenericFactoryAvro.get_factory_avro(
            reports_3_0_0.Pedigree, VERSION_300, fill_nullables=True
        ).create()
        for participant in old_instance.participants:
            for disorder in participant.disorderList:
                disorder.ageOfOnset = str(factory.fuzzy.FuzzyFloat(0.0).fuzz())
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)
        migrated_instance = MigrationHelpers.migrate_pedigree_to_version_1_0_3(
            old_instance.toJsonDict()
        )
        self._validate(migrated_instance)

    def test_migrate_pedigree_100_103(self):

        # tests IG participants 100 -> participants 103
        old_instance = GenericFactoryAvro.get_factory_avro(
            participant_1_0_0.Pedigree, VERSION_400, fill_nullables=True
        ).create()
        for member in old_instance.members:
            for disorder in member.disorderList:
                disorder.ageOfOnset = str(factory.fuzzy.FuzzyFloat(0.0).fuzz())
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_pedigree_to_version_1_0_3(
            old_instance.toJsonDict()
        )
        self._validate(migrated_instance)

    def test_migrate_pedigree_103_103(self):

        # tests pedigree participants 103 -> participants 103
        old_instance = GenericFactoryAvro.get_factory_avro(
            participant_1_0_3.Pedigree, VERSION_500, fill_nullables=True
        ).create()
        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        migrated_instance = MigrationHelpers.migrate_pedigree_to_version_1_0_3(
            old_instance.toJsonDict()
        )
        self._validate(migrated_instance)

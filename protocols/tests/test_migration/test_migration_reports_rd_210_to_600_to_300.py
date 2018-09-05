from protocols.util import dependency_manager
from protocols.util.factories.avro_factory import FactoryAvro, GenericFactoryAvro
from protocols.migration import MigrationHelpers, MigrateReports600To500, Migration21To3
from protocols import reports_2_1_0, reports_3_0_0, reports_6_0_0
from protocols.reports_6_0_0 import Assembly
from protocols.tests.test_migration.base_test_migration import BaseTestRoundTrip

import factory


class TestRoundTripMigrateReportsRd210To600(BaseTestRoundTrip):

    old_model = reports_2_1_0
    new_model = reports_6_0_0

    def test_migrate_rd_interpretation_request(self, fill_nullables=True):
        # get original IR in version 3.0.0
        assembly = Assembly.GRCh38
        original_ir = self.get_valid_object(
            object_type=reports_2_1_0.InterpretationRequestRD, version=self.version_2_1_0,
            fill_nullables=fill_nullables, genomeAssemblyVersion=assembly,
            versionControl=reports_2_1_0.VersionControl())
        for p in original_ir.pedigree.participants:
            p.gelFamilyId = original_ir.pedigree.gelFamilyId
        # migrates forward IR 3.0.0 into IG 6.0.0 and then back to IG 5.0.0
        ig6 = MigrationHelpers.migrate_interpretation_request_rd_to_interpreted_genome_latest(
            original_ir.toJsonDict(), assembly=assembly)
        ig5 = MigrateReports600To500().migrate_interpreted_genome_to_interpreted_genome_rd(ig6)
        self._check_round_trip_migration(
            MigrationHelpers.migrate_interpretation_request_rd_to_latest,
            MigrationHelpers.reverse_migrate_interpretation_request_rd_to_v3,
            Migration21To3().migrate_interpretation_request(original_ir),
            self.new_model.InterpretationRequestRD,
            expect_equality=True,
            ignore_fields=["analysisVersion", "analysisReturnURI", "SampleId", "cellbaseVersion",
                           "complexGeneticPhenomena", "interpretGenome", "ageOfOnset", "consanguineousPopulation",
                           "modifiers", "copyNumber"],
            forward_kwargs={'assembly': assembly},
            backward_kwargs={'ig_json_dict': ig5.toJsonDict()})

    def test_migrate_rd_interpretation_request_nulls(self):
        self.test_migrate_rd_interpretation_request(fill_nullables=False)

    def test_migrate_rd_interpreted_genome(self, fill_nullables=True):
        # get original IG in version 3.0.0
        # NOTE: we do not want to structural variants and we remove them to avoid noise
        original_ig = self.get_valid_object(
            object_type=reports_2_1_0.InterpretedGenomeRD, version=self.version_2_1_0,
            fill_nullables=fill_nullables,
            reportedStructuralVariants=[], versionControl=reports_3_0_0.VersionControl(), analysisId='1',
            reportURI=''
        )
        self._check_round_trip_migration(
            MigrationHelpers.migrate_interpreted_genome_rd_to_latest,
            MigrationHelpers.reverse_migrate_interpreted_genome_rd_to_v3,
            Migration21To3().migrate_interpreted_genome(original_ig),
            self.new_model.InterpretedGenome, expect_equality=True,
            ignore_fields=['additionalNumericVariantAnnotations', 'copyNumber'],
            forward_kwargs={'assembly': Assembly.GRCh38, 'interpretation_request_version': 1})

    def test_migrate_rd_interpreted_genome_nulls(self):
        self.test_migrate_rd_interpreted_genome(fill_nullables=False)

    def test_migrate_rd_clinical_report(self, fill_nullables=True):
        # get original IR in version 3.0.0
        original = self.get_valid_object(
            object_type=reports_2_1_0.ClinicalReportRD, version=self.version_2_1_0, fill_nullables=fill_nullables,
            interpretationRequestVersion='1', candidateStructuralVariants=[]
        )
        self._check_round_trip_migration(
            MigrationHelpers.migrate_clinical_report_rd_to_latest,
            MigrationHelpers.reverse_migrate_clinical_report_rd_to_v3,
            Migration21To3().migrate_clinical_report(original),
            self.new_model.ClinicalReport,
            expect_equality=True,
            ignore_fields=["interpretationRequestAnalysisVersion", "copyNumber", "genotype"],
            forward_kwargs={'assembly': Assembly.GRCh38})

    def test_migrate_rd_clinical_report_nulls(self):
        self.test_migrate_rd_clinical_report(fill_nullables=False)

    class FileFactory300(FactoryAvro):
        class Meta:
            model = reports_2_1_0.File

        _version = dependency_manager.VERSION_210

        SampleId = factory.fuzzy.FuzzyText()
        URIFile = factory.fuzzy.FuzzyText()
        fileType = factory.fuzzy.FuzzyChoice([reports_2_1_0.FileType.BAM, reports_2_1_0.FileType.BigWig,
                                              reports_2_1_0.FileType.ANN, reports_2_1_0.FileType.VCF_small])
        md5Sum = None

    def setUp(self):
        GenericFactoryAvro.register_factory(
            reports_3_0_0.File, self.FileFactory300, self.version_3_0_0, fill_nullables=True)
        GenericFactoryAvro.register_factory(
            reports_3_0_0.File, self.FileFactory300, self.version_3_0_0, fill_nullables=False)
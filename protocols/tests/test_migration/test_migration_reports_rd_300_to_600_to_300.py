from protocols import reports_6_0_0, reports_3_0_0
from protocols.reports_5_0_0 import Assembly
from protocols.migration import MigrateReports600To500
from protocols.tests.test_migration.migration_runner import MigrationRunner
from protocols.util.factories.avro_factory import FactoryAvro, GenericFactoryAvro
from protocols.migration.migration_helpers import MigrationHelpers
from protocols.tests.test_migration.base_test_migration import BaseTestRoundTrip
import factory.fuzzy
from protocols.util import dependency_manager
import random


class TestRoundTripMigrateReportsRd300To600(BaseTestRoundTrip):

    old_model = reports_3_0_0
    new_model = reports_6_0_0

    lateralities = [new_model.Laterality.RIGHT, new_model.Laterality.UNILATERAL, new_model.Laterality.BILATERAL,
                    new_model.Laterality.LEFT]
    progressions = [new_model.Progression.PROGRESSIVE, new_model.Progression.NONPROGRESSIVE]
    severities = [new_model.Severity.BORDERLINE, new_model.Severity.MILD, new_model.Severity.MODERATE,
                  new_model.Severity.SEVERE, new_model.Severity.PROFOUND]
    spatial_pattern = [new_model.SpatialPattern.DISTAL, new_model.SpatialPattern.GENERALIZED,
                       new_model.SpatialPattern.LOCALIZED, new_model.SpatialPattern.PROXIMAL]

    def _get_random_hpo_modifiers(self):
        values = [
            ('laterality', random.choice(self.lateralities)),
            ('progression', random.choice(self.progressions)),
            ('severity', random.choice(self.severities)),
            ('spatialPattern', random.choice(self.spatial_pattern))
            ]
        return dict(random.sample(values, random.randint(0, 4)))

    def test_migrate_rd_interpretation_request(self, fill_nullables=True):
        # get original IR in version 3.0.0
        assembly = Assembly.GRCh38
        original_ir = self.get_valid_object(
            object_type=reports_3_0_0.InterpretationRequestRD, version=self.version_3_0_0,
            fill_nullables=fill_nullables, genomeAssemblyVersion=assembly,
            versionControl=reports_3_0_0.VersionControl())  # type: reports_3_0_0.InterpretationRequestRD
        for p in original_ir.pedigree.participants:
            p.gelFamilyId = original_ir.pedigree.gelFamilyId
            p.yearOfBirth
        for p in original_ir.pedigree.participants:
            for hpo in p.hpoTermList:
                hpo.modifiers = self._get_random_hpo_modifiers()
        migrated, round_tripped = MigrationRunner().roundtrip_rd_ir(original_ir, assembly)
        self.assertFalse(self.diff_round_tripped(original_ir, round_tripped, ignore_fields=[
            "ageOfOnset", "consanguineousPopulation", "additionalInfo", "analysisVersion"]))

    def test_migrate_rd_interpretation_request_nulls(self):
        self.test_migrate_rd_interpretation_request(fill_nullables=False)

    def test_migrate_rd_interpreted_genome(self, fill_nullables=True):
        # get original IG in version 3.0.0
        # NOTE: we do not want to structural variants and we remove them to avoid noise
        original_ig = self.get_valid_object(
            object_type=reports_3_0_0.InterpretedGenomeRD, version=self.version_3_0_0, fill_nullables=fill_nullables,
            reportedStructuralVariants=None, versionControl=reports_3_0_0.VersionControl(), analysisId='1',
            reportURI='')
        migrated, round_tripped = MigrationRunner().roundtrip_rd_ig(original_ig, Assembly.GRCh38)
        self.assertFalse(self.diff_round_tripped(
            original_ig, round_tripped, ignore_fields=['additionalNumericVariantAnnotations']))

    def test_migrate_rd_interpreted_genome_nulls(self):
        self.test_migrate_rd_interpreted_genome(fill_nullables=False)

    def test_migrate_rd_clinical_report(self, fill_nullables=True):
        # get original IR in version 3.0.0
        original = self.get_valid_object(
            object_type=reports_3_0_0.ClinicalReportRD, version=self.version_3_0_0, fill_nullables=fill_nullables,
            interpretationRequestVersion='1', candidateStructuralVariants=None
        )
        migrated, round_tripped = MigrationRunner().roundtrip_rd_cr(original, Assembly.GRCh38)
        self.assertFalse(self.diff_round_tripped(
            original, round_tripped, ignore_fields=["interpretationRequestAnalysisVersion"]))

    def test_migrate_rd_clinical_report_nulls(self):
        self.test_migrate_rd_clinical_report(fill_nullables=False)

    def test_migrate_rd_exit_questionnaire(self, fill_nullables=True):
        original = self.get_valid_object(
            object_type=reports_3_0_0.RareDiseaseExitQuestionnaire, version=self.version_3_0_0,
            fill_nullables=fill_nullables)  # type: reports_3_0_0.RareDiseaseExitQuestionnaire
        for g in original.variantGroupLevelQuestions:
            for v in g.variantLevelQuestions:
                v.variant_details = self._get_random_variant_details()
        migrated, round_tripped = MigrationRunner().roundtrip_rd_eq(original, Assembly.GRCh38)
        self.assertFalse(self.diff_round_tripped(original, round_tripped, ignore_fields=[]))

    def test_migrate_rd_exit_questionnaire_nulls(self):
        self.test_migrate_rd_exit_questionnaire(fill_nullables=False)

    class FileFactory300(FactoryAvro):
        class Meta:
            model = reports_3_0_0.File

        _version = dependency_manager.VERSION_300

        SampleId = factory.fuzzy.FuzzyText()
        URIFile = factory.fuzzy.FuzzyText()
        fileType = factory.fuzzy.FuzzyChoice([reports_3_0_0.FileType.BAM, reports_3_0_0.FileType.BigWig,
                                              reports_3_0_0.FileType.ANN, reports_3_0_0.FileType.VCF_small])
        md5Sum = None

    class CalledGenotypeFactory300(FactoryAvro):
        class Meta:
            model = reports_3_0_0.CalledGenotype

        _version = dependency_manager.VERSION_300
        copyNumber = None

    class RDParticipantFactory300(FactoryAvro):
        class Meta:
            model = reports_3_0_0.RDParticipant

        _version = dependency_manager.VERSION_300
        versionControl = reports_3_0_0.VersionControl()
        yearOfBirth = str(factory.fuzzy.FuzzyInteger(low=1900, high=2018).fuzz())
        _fill_nullables = False

    class RDParticipantFactory300Nulls(FactoryAvro):
        class Meta:
            model = reports_3_0_0.RDParticipant

        _version = dependency_manager.VERSION_300
        versionControl = reports_3_0_0.VersionControl()
        yearOfBirth = str(factory.fuzzy.FuzzyInteger(low=1900, high=2018).fuzz())
        _fill_nullables = True

    class PedigreeFactory300(FactoryAvro):
        class Meta:
            model = reports_3_0_0.Pedigree

        _version = dependency_manager.VERSION_300
        versionControl = reports_3_0_0.VersionControl()
        _fill_nullables = False

    class PedigreeFactory300Nulls(FactoryAvro):
        class Meta:
            model = reports_3_0_0.Pedigree

        _version = dependency_manager.VERSION_300
        versionControl = reports_3_0_0.VersionControl()
        _fill_nullables = True

    class HpoTermFactory(FactoryAvro):
        class Meta:
            model = reports_3_0_0.HpoTerm

        _version = dependency_manager.VERSION_300
        _fill_nullables = True
        ageOfOnset = str(factory.fuzzy.FuzzyInteger(low=0, high=100).fuzz())

    def setUp(self):
        GenericFactoryAvro.register_factory(
            reports_3_0_0.File, self.FileFactory300, self.version_3_0_0, fill_nullables=True)
        GenericFactoryAvro.register_factory(
            reports_3_0_0.File, self.FileFactory300, self.version_3_0_0, fill_nullables=False)
        GenericFactoryAvro.register_factory(
            reports_3_0_0.CalledGenotype, self.CalledGenotypeFactory300, self.version_3_0_0, fill_nullables=True)
        GenericFactoryAvro.register_factory(
            reports_3_0_0.RDParticipant, self.RDParticipantFactory300, self.version_3_0_0, fill_nullables=False)
        GenericFactoryAvro.register_factory(
            reports_3_0_0.RDParticipant, self.RDParticipantFactory300Nulls, self.version_3_0_0, fill_nullables=True)
        GenericFactoryAvro.register_factory(
            reports_3_0_0.Pedigree, self.PedigreeFactory300, self.version_3_0_0, fill_nullables=False)
        GenericFactoryAvro.register_factory(
            reports_3_0_0.Pedigree, self.PedigreeFactory300Nulls, self.version_3_0_0, fill_nullables=True)
        GenericFactoryAvro.register_factory(
            reports_3_0_0.HpoTerm, self.HpoTermFactory, self.version_3_0_0, fill_nullables=True)

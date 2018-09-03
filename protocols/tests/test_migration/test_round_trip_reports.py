from protocols import reports_6_0_0, reports_4_0_0, reports_3_0_0, reports_2_1_0
from protocols.reports_5_0_0 import Assembly
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration import MigrateReports600To500, Migration21To3
from protocols.util.dependency_manager import VERSION_400
from protocols.util.factories.avro_factory import FactoryAvro, GenericFactoryAvro
from protocols.migration.migration_helpers import MigrationHelpers
import factory.fuzzy
from protocols.util import dependency_manager
import dictdiffer
import logging
import random


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


class BaseTestRoundTrip(TestCaseMigration):

    # all empty values will not be considered as mismatchs
    _empty_values = [None, [], {}, ""]
    _equal_values = {
        reports_3_0_0.Sex.undetermined: reports_3_0_0.Sex.unknown
    }

    def _check_round_trip_migration(self, forward, backward, original, new_type,
                                    expect_equality=True, ignore_fields=[],
                                    forward_kwargs={}, backward_kwargs={}):

        migrated = forward(original.toJsonDict(), **forward_kwargs)
        self.assertIsInstance(migrated, new_type)
        self.assertValid(migrated)

        round_tripped = backward(migrated.toJsonDict(), **backward_kwargs)
        self.assertIsInstance(round_tripped, type(original))
        self.assertValid(round_tripped)

        differ = False
        for diff_type, field_path, values in list(dictdiffer.diff(round_tripped.toJsonDict(), original.toJsonDict())):
            if type(field_path).__name__ in ['unicode', 'str']:
                field_path = [field_path]
            if BaseTestRoundTrip.is_field_ignored(field_path, ignore_fields):
                continue
            if isinstance(values, list):
                values = values[0]
            expected = values[1]
            observed = values[0]
            if observed in self._empty_values and expected in self._empty_values:
                continue
            if self._equal_values.get(expected, "not the same") == observed:
                continue
            logging.error("{}: {} expected '{}' found '{}'".format(diff_type, ".".join(list(map(str, field_path))), expected, observed))
            differ = True
        if expect_equality:
            self.assertFalse(differ)

    @staticmethod
    def is_field_ignored(field_path, ignored_fields):
        for ignored_field in ignored_fields:
            for path in field_path:
                if ignored_field in str(path):
                    return True
        return False

    def assertValid(self, instance):
        validation = instance.validate(instance.toJsonDict(), verbose=True)
        if not validation.result:
            for message in validation.messages:
                print(message)
            self.assertFalse(True)


class TestRoundTripMigrateReports300To600(BaseTestRoundTrip):

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

    # @unittest.skip
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
        # migrates forward IR 3.0.0 into IG 6.0.0 and then back to IG 5.0.0
        ig6 = MigrationHelpers.migrate_interpretation_request_rd_to_interpreted_genome_latest(
            original_ir.toJsonDict(), assembly=assembly)
        ig5 = MigrateReports600To500().migrate_interpreted_genome_to_interpreted_genome_rd(ig6)
        self._check_round_trip_migration(
            MigrationHelpers.migrate_interpretation_request_rd_to_latest,
            MigrationHelpers.reverse_migrate_interpretation_request_rd_to_v3,
            original_ir,
            self.new_model.InterpretationRequestRD,
            expect_equality=True, ignore_fields=["analysisVersion", "analysisReturnURI", "SampleId",
                                                 "cellbaseVersion", "complexGeneticPhenomena", "interpretGenome",
                                                 "ageOfOnset", "consanguineousPopulation"],
            forward_kwargs={'assembly': assembly},
            backward_kwargs={'ig_json_dict': ig5.toJsonDict()})

    # @unittest.skip
    def test_migrate_rd_interpretation_request_nulls(self):
        self.test_migrate_rd_interpretation_request(fill_nullables=False)

    def test_migrate_rd_interpreted_genome(self, fill_nullables=True):
        # get original IG in version 3.0.0
        # NOTE: we do not want to structural variants and we remove them to avoid noise
        original_ig = self.get_valid_object(
            object_type=reports_3_0_0.InterpretedGenomeRD, version=self.version_3_0_0, fill_nullables=fill_nullables,
            reportedStructuralVariants=None, versionControl=reports_3_0_0.VersionControl(), analysisId='1',
            reportURI=''
        )
        self._check_round_trip_migration(
            MigrationHelpers.migrate_interpreted_genome_rd_to_latest,
            MigrationHelpers.reverse_migrate_interpreted_genome_rd_to_v3,
            original_ig,
            self.new_model.InterpretedGenome,
            expect_equality=True, ignore_fields=['additionalNumericVariantAnnotations'],
            forward_kwargs={'assembly': Assembly.GRCh38, 'interpretation_request_version': 1})

    def test_migrate_rd_interpreted_genome_nulls(self):
        self.test_migrate_rd_interpreted_genome(fill_nullables=False)

    def test_migrate_rd_clinical_report(self, fill_nullables=True):
        # get original IR in version 3.0.0
        original = self.get_valid_object(
            object_type=reports_3_0_0.ClinicalReportRD, version=self.version_3_0_0, fill_nullables=fill_nullables,
            interpretationRequestVersion='1', candidateStructuralVariants=None
        )
        self._check_round_trip_migration(
            MigrationHelpers.migrate_clinical_report_rd_to_latest,
            MigrationHelpers.reverse_migrate_clinical_report_rd_to_v3,
            original,
            self.new_model.ClinicalReport,
            expect_equality=True, ignore_fields=["interpretationRequestAnalysisVersion"],
            forward_kwargs={'assembly': Assembly.GRCh38})

    def test_migrate_rd_clinical_report_nulls(self):
        self.test_migrate_rd_clinical_report(fill_nullables=False)

    @staticmethod
    def get_random_variant_details():
        reference, alternate = random.sample(['A', 'C', 'G', 'T'], 2)
        return "{chromosome}:{position}:{reference}:{alternate}".format(
            chromosome=random.randint(1, 22),
            position=random.randint(100, 1000000),
            reference=reference,
            alternate=alternate
        )

    def test_migrate_rd_exit_questionnaire(self, fill_nullables=True):
        original = self.get_valid_object(
            object_type=reports_3_0_0.RareDiseaseExitQuestionnaire, version=self.version_3_0_0,
            fill_nullables=fill_nullables)  # type: reports_3_0_0.RareDiseaseExitQuestionnaire
        for g in original.variantGroupLevelQuestions:
            for v in g.variantLevelQuestions:
                v.variant_details = self.get_random_variant_details()
        self._check_round_trip_migration(
            MigrationHelpers.migrate_exit_questionnaire_rd_to_latest,
            MigrationHelpers.reverse_migrate_exit_questionnaire_rd_to_v3,
            original,
            self.new_model.RareDiseaseExitQuestionnaire,
            expect_equality=True, ignore_fields=[],
            forward_kwargs={'assembly': Assembly.GRCh38})

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


class TestRoundTripMigrateReports210To600(BaseTestRoundTrip):

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

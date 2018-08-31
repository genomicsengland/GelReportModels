import unittest

from protocols import reports_6_0_0, reports_4_0_0, reports_5_0_0, reports_3_0_0
from protocols.migration import MigrateReports400To500, MigrateReports500To400
from protocols.reports_5_0_0 import Assembly
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_6_0_0_to_reports_5_0_0 import MigrateReports600To500
from protocols.migration.migration_reports_5_0_0_to_reports_6_0_0 import MigrateReports500To600
from protocols.util.dependency_manager import VERSION_400
from protocols.util.factories.avro_factory import FactoryAvro, GenericFactoryAvro
from protocols.migration.migration_helpers import MigrationHelpers
import factory.fuzzy
from protocols.util import dependency_manager
import dictdiffer
import logging
import factory


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
            if isinstance(field_path, unicode):
                field_path = [field_path]
            if BaseTestRoundTrip.is_field_ignored(field_path, ignore_fields):
                continue
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


# class TestRoundTripMigrateReports500To600(BaseTestRoundTrip):
#     old_model = reports_5_0_0
#     new_model = reports_6_0_0
#
#     def test_migrate_interpretation_request_rd(self):
#         self._check_rd(fill_nullables=True)
#
#     def test_migrate_interpretation_request_cancer(self):
#         self._check_cancer(fill_nullables=True)
#
#     def test_migrate_interpretation_request_rd_with_nulls(self):
#         self._check_rd(fill_nullables=False)
#
#     def test_migrate_interpretation_request_cancer_with_nulls(self):
#         self._check_cancer(fill_nullables=False)
#
#     def test_migrate_interpretated_genome_cancer(self):
#         self._check_round_trip_migration(
#             MigrateReports500To600().migrate_cancer_interpreted_genome,
#             MigrateReports600To500().migrate_cancer_interpreted_genome,
#             self.old_model.CancerInterpretedGenome,
#             self.new_model.InterpretedGenome,
#             fill_nullables=True,
#             original_version=self.version_6_1,
#             expect_equality=False
#         )
#
#     def test_migrate_interpretated_genome_cancer_with_nulls(self):
#         self._check_round_trip_migration(
#             MigrateReports500To600().migrate_cancer_interpreted_genome,
#             MigrateReports600To500().migrate_cancer_interpreted_genome,
#             self.old_model.CancerInterpretedGenome,
#             self.new_model.InterpretedGenome,
#             fill_nullables=False,
#             original_version=self.version_6_1,
#             expect_equality=False
#         )
#
#     def test_migrate_reported_variant_cancer(self):
#         self._check_round_trip_migration(
#             MigrateReports500To600().migrate_variant_cancer,
#             MigrateReports600To500().migrate_variant_cancer,
#             self.old_model.ReportedVariantCancer,
#             self.new_model.SmallVariant,
#             fill_nullables=True,
#             original_version=self.version_6_1,
#             expect_equality=False
#         )
#
#     def test_migrate_report_event_cancer_action(self):
#         self._check_round_trip_migration(
#             self._migrate_action,
#             lambda actions: MigrateReports600To500().migrate_actions(actions)[0],
#             self.old_model.Action,
#             self.new_model.Actions,
#             fill_nullables=True,
#             original_version=self.version_6_1,
#             expect_equality=False
#         )
#
#     def _migrate_action(self, action):
#         action.evidenceType = 'Trial (with, some, words)'
#         return MigrateReports500To600().migrate_actions([action])
#
#     def _check_cancer(self, fill_nullables):
#         self._check_round_trip_migration(
#             MigrateReports500To600().migrate_interpretation_request_cancer,
#             MigrateReports600To500().migrate_interpretation_request_cancer,
#             self.old_model.CancerInterpretationRequest,
#             self.new_model.CancerInterpretationRequest,
#             fill_nullables=fill_nullables,
#             original_version=self.version_6_1
#         )
#
#     def _check_rd(self, fill_nullables):
#         self._check_round_trip_migration(
#             MigrateReports500To600().migrate_interpretation_request_rd,
#             MigrateReports600To500().migrate_interpretation_request_rd,
#             self.old_model.InterpretationRequestRD,
#             self.new_model.InterpretationRequestRD,
#             fill_nullables=fill_nullables,
#             original_version=self.version_6_1
#         )
#
#
# class TestRoundTripMigrateReports400To600(BaseTestRoundTrip):
#     old_model = reports_4_0_0
#     new_model = reports_6_0_0
#
#     def test_migrate_cancer_interpreted_genome(self):
#         self._check_round_trip_migration(
#             self._migrate_cancer_interpreted_genome_forwards,
#             self._migrate_cancer_interpreted_genome_backwards,
#             self.old_model.CancerInterpretedGenome,
#             self.new_model.InterpretedGenome,
#             fill_nullables=True,
#             original_version=self.version_4_0_0,
#             expect_equality=False
#         )
#
#     def test_migrate_cancer_interpreted_genome_with_nulls(self):
#         self._check_round_trip_migration(
#             self._migrate_cancer_interpreted_genome_forwards,
#             self._migrate_cancer_interpreted_genome_backwards,
#             self.old_model.CancerInterpretedGenome,
#             self.new_model.InterpretedGenome,
#             fill_nullables=False,
#             original_version=self.version_4_0_0,
#             expect_equality=False
#         )
#
#     def _migrate_cancer_interpreted_genome_forwards(self, ig):
#         return MigrateReports500To600().migrate_cancer_interpreted_genome(
#                 MigrateReports400To500().migrate_cancer_interpreted_genome(
#                     old_instance=ig,
#                     assembly=Assembly.GRCh38,
#                     participant_id="pid",
#                     sample_id="sid",
#                     interpretation_request_version=12345,
#                     interpretation_service="testing"
#                 )
#             )
#
#     def _migrate_cancer_interpreted_genome_backwards(self, ig):
#         return MigrateReports500To400().migrate_cancer_interpreted_genome(
#                 MigrateReports600To500().migrate_cancer_interpreted_genome(ig)
#             )
#
#     def setUp(self):
#         GenericFactoryAvro.register_factory(
#             reports_4_0_0.Actions, ActionFactory, VERSION_400, fill_nullables=True)
#         GenericFactoryAvro.register_factory(
#             reports_4_0_0.Actions, ActionFactory, VERSION_400, fill_nullables=False)


class TestRoundTripMigrateReports300To600(BaseTestRoundTrip):

    old_model = reports_3_0_0
    new_model = reports_6_0_0

    # @unittest.skip
    def test_migrate_rd_interpretation_request(self, fill_nullables=True):
        # get original IR in version 3.0.0
        assembly = Assembly.GRCh38
        original_ir = self.get_valid_object(
            object_type=reports_3_0_0.InterpretationRequestRD, version=self.version_3_0_0,
            fill_nullables=fill_nullables, genomeAssemblyVersion=assembly,
            versionControl=reports_3_0_0.VersionControl())
        for p in original_ir.pedigree.participants:
            p.gelFamilyId = original_ir.pedigree.gelFamilyId
            p.yearOfBirth
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
                                                 "ageOfOnset", "consanguineousPopulation", "modifiers"],
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

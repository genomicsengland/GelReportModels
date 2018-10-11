from protocols import reports_6_0_0, reports_5_0_0, reports_4_0_0, reports_3_0_0, participant_1_0_0
from protocols.reports_5_0_0 import Assembly
from protocols.util.factories.avro_factory import FactoryAvro, GenericFactoryAvro
from protocols.migration.migration_helpers import MigrationHelpers
from protocols.tests.test_migration.base_test_migration import BaseTestRoundTrip
from protocols.tests.test_migration.migration_runner import MigrationRunner
import factory.fuzzy
from protocols.util import dependency_manager
import random
from itertools import chain


class TestRoundTripMigrateReportsCancer400To600(BaseTestRoundTrip):

    old_model = reports_3_0_0
    new_model = reports_6_0_0

    @staticmethod
    def _get_random_variant_details():
        reference, alternate = random.sample(['A', 'C', 'G', 'T'], 2)
        return "{chromosome}:{position}:{reference}:{alternate}".format(
            chromosome=random.randint(1, 22),
            position=random.randint(100, 1000000),
            reference=reference,
            alternate=alternate
        )

    def test_migrate_cancer_interpretation_request(self, fill_nullables=True):
        # get original IR in version 4.0.0
        assembly = Assembly.GRCh38
        original_ir = self.get_valid_object(
            object_type=reports_4_0_0.CancerInterpretationRequest, version=self.version_4_0_0,
            fill_nullables=fill_nullables, genomeAssemblyVersion=assembly, structuralTieredVariants=[],
            versionControl=reports_4_0_0.ReportVersionControl(gitVersionControl='4.0.0')
        )
        valid_cancer_origins = ['germline_variant', 'somatic_variant']
        for tiered_variant in original_ir.tieredVariants:
            if tiered_variant.alleleOrigins[0] not in valid_cancer_origins:
                tiered_variant.alleleOrigins[0] = random.choice(valid_cancer_origins)
        # # migration requires there is exactly one tumour sample
        original_ir.cancerParticipant.tumourSamples = [original_ir.cancerParticipant.tumourSamples[0]]
        migrated, round_tripped = MigrationRunner().roundtrip_cancer_ir(original_ir, assembly)
        self.assertFalse(self.diff_round_tripped(original_ir, round_tripped, ignore_fields=[
            "TNMStageVersion", "TNMStageGrouping", "actions",
            "additionalTextualVariantAnnotations", "matchedSamples", "commonAf", "additionalInfo"]))
        # NOTE: not all fields in actions are kept and the order is not maintained, thus we ignore it in the
        # dictionary comparison and then here manually check them
        expected_report_events = chain.from_iterable(
            map(lambda v: [re for re in v.reportedVariantCancer.reportEvents], original_ir.tieredVariants))
        observed_report_events = chain.from_iterable(
            map(lambda v: [re for re in v.reportedVariantCancer.reportEvents], round_tripped.tieredVariants))
        self.assertFalse(self.diff_actions(chain(expected_report_events, observed_report_events)))

    def test_migrate_cancer_interpretation_request_nulls(self):
        self.test_migrate_cancer_interpretation_request(fill_nullables=False)

    def test_migrate_cancer_interpreted_genome(self, fill_nullables=True):
        assembly = Assembly.GRCh38
        original_ig = self.get_valid_object(
            object_type=reports_4_0_0.CancerInterpretedGenome, version=self.version_4_0_0,
            fill_nullables=fill_nullables, genomeAssemblyVersion=assembly,
            interpretGenome=True, reportedStructuralVariants=[],
            versionControl=reports_4_0_0.ReportVersionControl(gitVersionControl='4.0.0')
        )
        valid_cancer_origins = ['germline_variant', 'somatic_variant']
        for reported_variant in original_ig.reportedVariants:
            if reported_variant.alleleOrigins[0] not in valid_cancer_origins:
                reported_variant.alleleOrigins[0] = random.choice(valid_cancer_origins)
        # migration requires there is exactly one tumour sample
        migrated, round_tripped = MigrationRunner().roundtrip_cancer_ig(original_ig, assembly)
        self.assertFalse(self.diff_round_tripped(original_ig, round_tripped, ignore_fields=[
            "analysisId", "actions", "additionalTextualVariantAnnotations", "commonAf"]))

        # NOTE: not all fields in actions are kept and the order is not maintained, thus we ignore it in the
        # dictionary comparison and then here manually check them
        expected_report_events = chain.from_iterable(
            map(lambda v: [re for re in v.reportedVariantCancer.reportEvents], original_ig.reportedVariants))
        observed_report_events = chain.from_iterable(
            map(lambda v: [re for re in v.reportedVariantCancer.reportEvents], round_tripped.reportedVariants))
        self.assertFalse(self.diff_actions(chain(expected_report_events, observed_report_events)))

    def test_migrate_cancer_interpreted_genome_nulls(self):
        self.test_migrate_cancer_interpreted_genome(fill_nullables=False)

    def test_migrate_cancer_clinical_report(self, fill_nullables=True):
        assembly = Assembly.GRCh38
        original_cr = self.get_valid_object(
            object_type=reports_4_0_0.ClinicalReportCancer, version=self.version_4_0_0,
            fill_nullables=fill_nullables, genomeAssemblyVersion=assembly,
            interpretGenome=True, candidateStructuralVariants=[],
            versionControl=reports_4_0_0.ReportVersionControl(gitVersionControl='4.0.0'),
            interpretationRequestVersion='123'
        )

        valid_cancer_origins = ['germline_variant', 'somatic_variant']
        if original_cr.candidateVariants:
            for candidate_variant in original_cr.candidateVariants:
                if candidate_variant.alleleOrigins[0] not in valid_cancer_origins:
                    candidate_variant.alleleOrigins[0] = random.choice(valid_cancer_origins)

        migrated, round_tripped = MigrationRunner().roundtrip_cancer_cr(original_cr, assembly)
        self.assertFalse(self.diff_round_tripped(original_cr, round_tripped, ignore_fields=[
            "analysisId", "actions", "additionalTextualVariantAnnotations", "commonAf", "genePanelsCoverage"]))
        # NOTE: not all fields in actions are kept and the order is not maintained, thus we ignore it in the
        # dictionary comparison and then here manually check them
        if original_cr.candidateVariants:
            expected_report_events = chain.from_iterable(
                map(lambda v: [re for re in v.reportedVariantCancer.reportEvents], original_cr.candidateVariants))
        else:
            expected_report_events = []
        if round_tripped.candidateVariants:
            observed_report_events = chain.from_iterable(
                map(lambda v: [re for re in v.reportedVariantCancer.reportEvents], round_tripped.candidateVariants))
        else:
            observed_report_events = []
        self.assertFalse(self.diff_actions(chain(expected_report_events, observed_report_events)))

    def test_migrate_cancer_clinical_report_nulls(self):
        self.test_migrate_cancer_clinical_report(fill_nullables=False)

    def test_migrate_cancer_exit_questionnaire(self, fill_nullables=True):
        assembly = Assembly.GRCh38
        original_eq = self.get_valid_object(
            object_type=reports_5_0_0.CancerExitQuestionnaire, version=self.version_6_1,
            fill_nullables=fill_nullables,
            versionControl=reports_5_0_0.ReportVersionControl()
        )
        if original_eq.somaticVariantLevelQuestions:
            for q in original_eq.somaticVariantLevelQuestions:
                q.variantDetails = self._get_random_variant_details()
        if original_eq.germlineVariantLevelQuestions:
            for q in original_eq.germlineVariantLevelQuestions:
                q.variantDetails = self._get_random_variant_details()
        if original_eq.otherActionableVariants:
            for q in original_eq.otherActionableVariants:
                q.variantDetails = self._get_random_variant_details()
        migrated, round_tripped = MigrationRunner().roundtrip_cancer_eq(original_eq, assembly)
        self.diff_round_tripped(original_eq, round_tripped, ignore_fields=[])

    def test_migrate_cancer_exit_questionnaire_nulls(self):
        self.test_migrate_cancer_exit_questionnaire(fill_nullables=False)

    class ActionFactory(FactoryAvro):
        class Meta:
            model = reports_4_0_0.Actions

        _version = dependency_manager.VERSION_400

        actionType = factory.fuzzy.FuzzyChoice(
            ['Trial (blah, blah)', 'Therapeutic (blah, blah)', 'Prognostic (blah, blah)'])
        status = factory.fuzzy.FuzzyChoice(['clinical', 'pre-clinical'])
        evidence = None
        drug = None
        variantActionable = factory.fuzzy.FuzzyChoice([True, False])
        comments = None
        url = factory.fuzzy.FuzzyText()
        evidenceType = None
        source = factory.fuzzy.FuzzyText()

    class CancerParticipantFactory(FactoryAvro):
        class Meta:
            model = participant_1_0_0.CancerParticipant

        _version = dependency_manager.VERSION_400
        _fill_nullables = False
        versionControl = participant_1_0_0.VersionControl(GitVersionControl='1.0.0')

    class CancerParticipantFactoryNulls(FactoryAvro):
        class Meta:
            model = participant_1_0_0.CancerParticipant

        _version = dependency_manager.VERSION_400
        _fill_nullables = True
        versionControl = participant_1_0_0.VersionControl(GitVersionControl='1.0.0')

    def setUp(self):
        GenericFactoryAvro.register_factory(
            reports_4_0_0.Actions, self.ActionFactory, self.version_4_0_0, fill_nullables=True)
        GenericFactoryAvro.register_factory(
            reports_4_0_0.Actions, self.ActionFactory, self.version_4_0_0, fill_nullables=False)
        GenericFactoryAvro.register_factory(
            participant_1_0_0.CancerParticipant, self.CancerParticipantFactory, self.version_4_0_0, fill_nullables=False)
        GenericFactoryAvro.register_factory(
            participant_1_0_0.CancerParticipant, self.CancerParticipantFactoryNulls, self.version_4_0_0, fill_nullables=True)

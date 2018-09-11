#!/usr/bin/env python
from protocols_utils.utils.abstract_migration_test_real_data import AbstractRealRoundTripper
from protocols import reports_4_0_0, reports_5_0_0, reports_6_0_0
from protocols.migration.base_migration import MigrationError
from protocols.reports_6_0_0 import Program
from itertools import chain
import time


class RealRoundTripperCancer(AbstractRealRoundTripper):

    def __init__(self):
        super(RealRoundTripperCancer, self).__init__(
            "real_data_cancer_round_trip.log", Program.cancer, "data", use_data=True)

    def _check_actions(self, original_reported_variants, round_tripped_reported_variants):
        expected_report_events = chain.from_iterable(
            map(lambda v: [re for re in v.reportedVariantCancer.reportEvents], original_reported_variants))
        observed_report_events = chain.from_iterable(
            map(lambda v: [re for re in v.reportedVariantCancer.reportEvents], round_tripped_reported_variants))
        return self.migration_runner.diff_actions(chain(expected_report_events, observed_report_events))

    def process_case(self, case):
        # interpretation request
        raw_ir = case.raw_interpretation_request
        case_id = case.case_id
        case_version = case.case_version
        ir = reports_4_0_0.CancerInterpretationRequest.fromJsonDict(raw_ir)
        try:
            start = int(round(time.time() * 1000))
            ir_migrated, ir_round_tripped = self.migration_runner.roundtrip_cancer_ir(ir, case.assembly)
            run_time = int(round(time.time() * 1000)) - start
            is_valid = ir_migrated.validate(reports_6_0_0.CancerInterpretationRequest, ir_migrated.toJsonDict())
            is_valid_round_tripped = ir_round_tripped.validate(
                reports_4_0_0.CancerInterpretationRequest, ir_round_tripped.toJsonDict())
            differ = self.migration_runner.diff_round_tripped(
                ir, ir_round_tripped,
                ignore_fields=["TNMStageVersion", "TNMStageGrouping",
                               "additionalTextualVariantAnnotations", "matchedSamples", "commonAf",
                               "actions",  # NOTE: this is ignores as actions come back in a different order
                               "versionControl",  # NOTE: this is ignored as some real data have a missing version value
                               "additionalInfo"
                               ])
            differ |= self._check_actions(ir.tieredVariants, ir_round_tripped.tieredVariants)
            RealRoundTripperCancer.log_case(
                "IR", case_id, case_version, '4.0.0', differ, is_valid, is_valid_round_tripped, run_time)
        except MigrationError as e:
            RealRoundTripperCancer.log("MIGRATION_ERROR", "IR", '4.0.0', case_id, case_version, e.message)

        # interpreted genome
        if case.has_interpreted_genome():
            ig = reports_4_0_0.CancerInterpretedGenome.fromJsonDict(
                case.raw_interpreted_genome)  # type: reports_4_0_0.CancerInterpretedGenome
            try:
                start = int(round(time.time() * 1000))
                ig_migrated, ig_round_tripped = self.migration_runner.roundtrip_cancer_ig(ig, case.assembly)
                run_time = int(round(time.time() * 1000)) - start
                is_valid = ig_migrated.validate(reports_6_0_0.InterpretedGenome, ig_migrated.toJsonDict())
                is_valid_round_tripped = ig_round_tripped.validate(
                    reports_4_0_0.CancerInterpretedGenome, ig_round_tripped.toJsonDict())
                differ = self.migration_runner.diff_round_tripped(
                    ig, ig_round_tripped, ignore_fields=["analysisId", "additionalTextualVariantAnnotations", "commonAf"])
                differ |= self._check_actions(ig.reportedVariants, ig_round_tripped.reportedVariants)
                RealRoundTripperCancer.log_case(
                    "IG", case_id, case_version, '4.0.0', differ, is_valid, is_valid_round_tripped, run_time)
            except MigrationError as e:
                RealRoundTripperCancer.log("MIGRATION_ERROR", "IG", '4.0.0', case_id, case_version, e.message)

        # clinical report
        if case.has_clinical_report():
            cr = reports_4_0_0.ClinicalReportCancer.fromJsonDict(
                case.raw_clinical_report)  # type: reports_4_0_0.ClinicalReportCancer
            try:
                start = int(round(time.time() * 1000))
                cr_migrated, cr_round_tripped = self.migration_runner.roundtrip_cancer_cr(cr, case.assembly)
                run_time = int(round(time.time() * 1000)) - start
                is_valid = cr_migrated.validate(reports_6_0_0.ClinicalReport, cr_migrated.toJsonDict())
                is_valid_round_tripped = cr_round_tripped.validate(
                    reports_4_0_0.ClinicalReportCancer, cr_round_tripped.toJsonDict())
                differ = self.migration_runner.diff_round_tripped(
                    cr, cr_round_tripped, ignore_fields=["analysisId", "additionalTextualVariantAnnotations", "commonAf",
                                                         "genePanelsCoverage", "actions"])
                differ |= self._check_actions(cr.candidateVariants, cr_round_tripped.candidateVariants)
                RealRoundTripperCancer.log_case(
                    "CR", case_id, case_version, '4.0.0', differ, is_valid, is_valid_round_tripped, run_time)
            except MigrationError as e:
                RealRoundTripperCancer.log("MIGRATION_ERROR", "CR", '4.0.0', case_id, case_version, e.message)

        if case.has_exit_questionnaire():
            eq = reports_5_0_0.CancerExitQuestionnaire.fromJsonDict(case.raw_questionnaire)
            try:
                start = int(round(time.time() * 1000))
                eq_migrated, eq_round_tripped = self.migration_runner.roundtrip_cancer_eq(eq, case.assembly)
                run_time = int(round(time.time() * 1000)) - start
                is_valid = eq_migrated.validate(reports_6_0_0.CancerExitQuestionnaire, eq_migrated.toJsonDict())
                is_valid_round_tripped = eq_round_tripped.validate(
                    reports_5_0_0.CancerExitQuestionnaire, eq_round_tripped.toJsonDict())
                differ = self.migration_runner.diff_round_tripped(
                    eq, eq_round_tripped, ignore_fields=[])
                RealRoundTripperCancer.log_case(
                    "EQ", case_id, case_version, '5.0.0', differ, is_valid, is_valid_round_tripped, run_time)
            except MigrationError as e:
                RealRoundTripperCancer.log("MIGRATION_ERROR", "EQ", '5.0.0', case_id, case_version, e.message)

if __name__ == '__main__':
    round_tripper = RealRoundTripperCancer()
    round_tripper.run()

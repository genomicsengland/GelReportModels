#!/usr/bin/env python
from protocols import reports_2_1_0, reports_3_0_0, reports_6_0_0
from protocols.migration import Migration21To3
from protocols.migration.base_migration import MigrationError
from protocols.reports_6_0_0 import Program
from protocols_utils.utils.abstract_migration_test_real_data import AbstractRealRoundTripper


class RealRoundTripperRd(AbstractRealRoundTripper):

    def __init__(self):
        super(RealRoundTripperRd, self).__init__("real_data_rd_round_trip.log", Program.rare_disease, "data")

    def process_case(self, case):
        # interpretation request
        raw_ir, case_id, version = case._get_raw_interpretation_request()
        try:
            ir = reports_2_1_0.InterpretationRequestRD.fromJsonDict(raw_ir)
            model_version = '3.0.0'
            if ir.versionControl.GitVersionControl == '2.1.0':
                model_version = '2.1.0'
                ir = Migration21To3().migrate_interpretation_request(
                    reports_2_1_0.InterpretationRequestRD.fromJsonDict(raw_ir))
            else:
                ir = reports_3_0_0.InterpretationRequestRD.fromJsonDict(raw_ir)
            ir_migrated, ir_round_tripped = self.migration_runner.roundtrip_rd_ir(ir, case.assembly)
            is_valid = ir_migrated.validate(reports_6_0_0.InterpretationRequestRD, ir_migrated.toJsonDict())
            is_valid_round_tripped = ir_round_tripped.validate(
                reports_3_0_0.InterpretationRequestRD, ir_round_tripped.toJsonDict())
            differ = self.migration_runner.diff_round_tripped(
                ir, ir_round_tripped,
                ignore_fields=[
                    "ageOfOnset", "consanguineousPopulation", "reportUri", "GitVersionControl",
                    "analysisId", "genomeAssemblyVersion", "modifiers", "additionalInfo"
                ])
            RealRoundTripperRd.log_case("IR", case_id, version, model_version, differ, is_valid, is_valid_round_tripped)
        except MigrationError as e:
            RealRoundTripperRd.log("MIGRATION_ERROR", "IR", model_version, case_id, version, e.message)

        # interpreted genome
        if case.has_interpreted_genome():
            raw_ig = case.raw_interpreted_genome
            try:
                is_valid_210 = reports_2_1_0.InterpretedGenomeRD.validate(
                    reports_2_1_0.InterpretedGenomeRD, reports_2_1_0.InterpretedGenomeRD.fromJsonDict(raw_ir))
                is_valid_300 = reports_3_0_0.InterpretedGenomeRD.validate(
                    reports_3_0_0.InterpretedGenomeRD, reports_3_0_0.InterpretedGenomeRD.fromJsonDict(raw_ir))
                if is_valid_210 and not is_valid_300:
                    model_version = '2.1.0'
                    ig = reports_2_1_0.InterpretedGenomeRD.fromJsonDict(raw_ir)
                    ig = Migration21To3().migrate_interpreted_genome(ig)
                elif is_valid_300:
                    model_version = '3.0.0'
                    ig = reports_3_0_0.InterpretedGenomeRD.fromJsonDict(raw_ig)
                else:
                    raise MigrationError("Payload invalid according to 2.1.0 and 3.0.0")
                ig_migrated, ig_round_tripped = self.migration_runner.roundtrip_rd_ig(ig, case.assembly)
                is_valid = ig_migrated.validate(reports_6_0_0.InterpretedGenome, ig_migrated.toJsonDict())
                is_valid_round_tripped = ig_round_tripped.validate(
                    reports_3_0_0.InterpretedGenomeRD, ig_round_tripped.toJsonDict())
                differ = self.migration_runner.diff_round_tripped(
                    ig, ig_round_tripped,
                    ignore_fields=['additionalNumericVariantAnnotations', "reportURI", "analysisId",
                                   "GitVersionControl"])
                RealRoundTripperRd.log_case("IG", case_id, version, model_version, differ, is_valid,
                                            is_valid_round_tripped)
            except MigrationError as e:
                RealRoundTripperRd.log("MIGRATION_ERROR", "IG", model_version, case_id, version, e.message)

        # clinical report
        if case.has_clinical_report():
            raw_cr = case.raw_clinical_report
            try:
                model_version = '3.0.0'
                if reports_2_1_0.ClinicalReportRD.validate(
                        reports_2_1_0.InterpretedGenomeRD, reports_2_1_0.InterpretedGenomeRD.fromJsonDict(raw_cr)):
                    model_version = '2.1.0'
                    cr = Migration21To3().migrate_clinical_report(reports_2_1_0.ClinicalReportRD.fromJsonDict(raw_cr))
                else:
                    cr = reports_3_0_0.ClinicalReportRD.fromJsonDict(raw_cr)
                cr_migrated, cr_round_tripped = self.migration_runner.roundtrip_rd_cr(cr, case.assembly)
                is_valid = cr_migrated.validate(reports_6_0_0.ClinicalReport, cr_migrated.toJsonDict())
                is_valid_round_tripped = cr_round_tripped.validate(
                    reports_3_0_0.ClinicalReportRD, cr_round_tripped.toJsonDict())
                differ = self.migration_runner.diff_round_tripped(
                    cr, cr_round_tripped, ignore_fields=["interpretationRequestAnalysisVersion", "GitVersionControl"])
                RealRoundTripperRd.log_case("CR", case_id, version, model_version, differ, is_valid,
                                            is_valid_round_tripped)
            except MigrationError as e:
                RealRoundTripperRd.log("MIGRATION_ERROR", "CR", model_version, case_id, version, e.message)

        if case.has_exit_questionnaire():
            raw_eq = case.raw_questionnaire
            eq = reports_3_0_0.RareDiseaseExitQuestionnaire.fromJsonDict(raw_eq)
            try:
                eq_migrated, eq_round_tripped = self.migration_runner.roundtrip_rd_eq(eq, case.assembly)
                is_valid = eq_migrated.validate(reports_6_0_0.RareDiseaseExitQuestionnaire, eq_migrated.toJsonDict())
                is_valid_round_tripped = eq_round_tripped.validate(
                    reports_3_0_0.RareDiseaseExitQuestionnaire, eq_round_tripped.toJsonDict())
                differ = self.migration_runner.diff_round_tripped(
                    eq, eq_round_tripped, ignore_fields=[])
                RealRoundTripperRd.log_case("EQ", case_id, version, '3.0.0', differ, is_valid,
                                            is_valid_round_tripped)
            except MigrationError as e:
                RealRoundTripperRd.log("MIGRATION_ERROR", "EQ", '3.0.0', case_id, version, e.message)


if __name__ == '__main__':
    round_tripper = RealRoundTripperRd()
    round_tripper.run()

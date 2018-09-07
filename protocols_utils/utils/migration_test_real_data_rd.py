#!/usr/bin/env python
from pycipapi.cipapi_client import CipApiClient, CipApiCase
import getpass
from protocols import reports_2_1_0, reports_3_0_0, reports_6_0_0
from protocols.migration import Migration21To3
from protocols.migration.base_migration import MigrationError
from protocols.reports_6_0_0 import Program
from protocols.tests.test_migration.migration_runner import MigrationRunner
import logging


class RealRoundTripperRd(object):

    def __init__(self):
        # configures logging to get only logs about the failed cases
        self.log_file = "real_data_rd_round_trip.log"
        logging.basicConfig(filename=self.log_file, level=logging.ERROR)
        gel_user = raw_input("User:")
        gel_password = getpass.getpass("Password:")
        cipapi_url = raw_input("URL:")
        self.cipapi_client = CipApiClient(cipapi_url, user=gel_user, password=gel_password, retries=-1)
        self.migration_runner = MigrationRunner()

    def process_case(self, case):
        # interpretation request
        raw_ir, case_id, version = case._get_raw_interpretation_request()
        ir = reports_2_1_0.InterpretationRequestRD.fromJsonDict(raw_ir)
        if ir.versionControl.GitVersionControl == '2.1.0':
            ir = Migration21To3().migrate_interpretation_request(
                reports_2_1_0.InterpretationRequestRD.fromJsonDict(raw_ir))
        else:
            ir = reports_3_0_0.InterpretationRequestRD.fromJsonDict(raw_ir)

        try:
            ir_migrated, ir_round_tripped = self.migration_runner.roundtrip_rd_ir(ir, case.assembly)
        except MigrationError as e:
            logging.error("Skipping case {}-{}: {}".format(case_id, version, e.message))
            return

        is_valid = ir_migrated.validate(reports_6_0_0.InterpretationRequestRD, ir_migrated.toJsonDict())
        is_valid_round_tripped = ir_round_tripped.validate(
            reports_3_0_0.InterpretationRequestRD, ir_round_tripped.toJsonDict())
        differ = self.migration_runner.diff_round_tripped(
            ir, ir_round_tripped,
            ignore_fields=[
                "ageOfOnset", "consanguineousPopulation", "reportUri", "GitVersionControl",
                "analysisId", "genomeAssemblyVersion", "modifiers", "additionalInfo"
            ])

        if not is_valid:
            logging.error("Invalid rd IR {}-{}".format(case_id, version))
        if not is_valid_round_tripped:
            logging.error("Invalid round tripped rd IR {}-{}".format(case_id, version))
        logging.error("{} rd IR {}-{}".format("KO" if differ else "OK", case_id, version))

        # interpreted genome
        if case.has_interpreted_genome():
            raw_ig = case.raw_interpreted_genome
            if reports_2_1_0.InterpretedGenomeRD.validate(
                    reports_2_1_0.InterpretedGenomeRD, reports_2_1_0.InterpretedGenomeRD.fromJsonDict(raw_ig)):
                ig = Migration21To3().migrate_interpreted_genome(
                    reports_2_1_0.InterpretedGenomeRD.fromJsonDict(raw_ig))
            else:
                ig = reports_3_0_0.InterpretedGenomeRD.fromJsonDict(raw_ig)  # type: reports_3_0_0.InterpretedGenomeRD
            ig_migrated, ig_round_tripped = self.migration_runner.roundtrip_rd_ig(ig, case.assembly)
            is_valid = ig_migrated.validate(reports_6_0_0.InterpretedGenome, ig_migrated.toJsonDict())
            is_valid_round_tripped = ig_round_tripped.validate(
                reports_3_0_0.InterpretedGenomeRD, ig_round_tripped.toJsonDict())
            differ = self.migration_runner.diff_round_tripped(
                ig, ig_round_tripped, ignore_fields=['additionalNumericVariantAnnotations', "reportURI", "analysisId",
                                                     "GitVersionControl"])
            if not is_valid:
                logging.error("Invalid rd IG {}-{}".format(case_id, version))
            if not is_valid_round_tripped:
                logging.error("Invalid round tripped rd IG {}-{}".format(case_id, version))
            logging.error("{} rd IG {}-{}".format("KO" if differ else "OK", case_id, version))

        # clinical report
        if case.has_clinical_report():
            raw_cr = case.raw_clinical_report
            if reports_2_1_0.ClinicalReportRD.validate(
                    reports_2_1_0.InterpretedGenomeRD, reports_2_1_0.InterpretedGenomeRD.fromJsonDict(raw_cr)):
                cr = Migration21To3().migrate_clinical_report(reports_2_1_0.ClinicalReportRD.fromJsonDict(raw_cr))
            else:
                cr = reports_3_0_0.ClinicalReportRD.fromJsonDict(raw_cr)  # type: reports_3_0_0.ClinicalReportRD
            cr_migrated, cr_round_tripped = self.migration_runner.roundtrip_rd_cr(cr, case.assembly)
            is_valid = cr_migrated.validate(reports_6_0_0.ClinicalReport, cr_migrated.toJsonDict())
            is_valid_round_tripped = cr_round_tripped.validate(
                reports_3_0_0.ClinicalReportRD, cr_round_tripped.toJsonDict())
            differ = self.migration_runner.diff_round_tripped(
                cr, cr_round_tripped, ignore_fields=["interpretationRequestAnalysisVersion", "GitVersionControl"])
            if not is_valid:
                logging.error("Invalid rd CR {}-{}".format(case_id, version))
            if not is_valid_round_tripped:
                logging.error("Invalid round tripped rd CR {}-{}".format(case_id, version))
            logging.error("{} rd CR {}-{}".format("KO" if differ else "OK", case_id, version))

        if case.has_exit_questionnaire():
            raw_eq = case.raw_questionnaire
            eq = reports_3_0_0.RareDiseaseExitQuestionnaire.fromJsonDict(raw_eq)  # type: reports_3_0_0.RareDiseaseExitQuestionnaire
            eq_migrated, eq_round_tripped = self.migration_runner.roundtrip_rd_eq(eq, case.assembly)
            is_valid = eq_migrated.validate(reports_6_0_0.RareDiseaseExitQuestionnaire, eq_migrated.toJsonDict())
            is_valid_round_tripped = eq_round_tripped.validate(
                reports_3_0_0.RareDiseaseExitQuestionnaire, eq_round_tripped.toJsonDict())
            differ = self.migration_runner.diff_round_tripped(
                eq, eq_round_tripped, ignore_fields=[])
            if not is_valid:
                logging.error("Invalid rd EQ {}-{}".format(case_id, version))
            if not is_valid_round_tripped:
                logging.error("Invalid round tripped rd EQ {}-{}".format(case_id, version))
            logging.error("{} rd EQ {}-{}".format("KO" if differ else "OK", case_id, version))

    def run(self):
        print "Check your results in '{}'".format(self.log_file)
        for case in self.cipapi_client.get_cases(program=Program.rare_disease):  # type: CipApiCase
            self.process_case(case)


if __name__ == '__main__':
    round_tripper = RealRoundTripperRd()
    round_tripper.run()

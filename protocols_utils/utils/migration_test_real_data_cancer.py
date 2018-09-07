#!/usr/bin/env python
from pycipapi.cipapi_client import CipApiClient, CipApiCase
import getpass
from protocols import reports_4_0_0, reports_6_0_0
from protocols.migration.base_migration import MigrationError
from protocols.reports_6_0_0 import Program
from protocols.tests.test_migration.migration_runner import MigrationRunner
from itertools import chain
import logging


class RealRoundTripperCancer(object):

    def __init__(self):
        # configures logging to get only logs about the failed cases
        self.log_file = "real_data_cancer_round_trip.log"
        logging.basicConfig(filename=self.log_file, level=logging.ERROR)
        gel_user = raw_input("User:")
        gel_password = getpass.getpass("Password:")
        cipapi_url = raw_input("URL:")
        self.cipapi_client = CipApiClient(cipapi_url, user=gel_user, password=gel_password, retries=-1)
        self.migration_runner = MigrationRunner()

    def _check_actions(self, original_reported_variants, round_tripped_reported_variants):
        expected_report_events = chain.from_iterable(
            map(lambda v: [re for re in v.reportedVariantCancer.reportEvents], original_reported_variants))
        observed_report_events = chain.from_iterable(
            map(lambda v: [re for re in v.reportedVariantCancer.reportEvents], round_tripped_reported_variants))
        return self.migration_runner.diff_actions(chain(expected_report_events, observed_report_events))

    def process_case(self, case):
        # interpretation request
        raw_ir, case_id, version = case._get_raw_interpretation_request()
        ir = reports_4_0_0.CancerInterpretationRequest.fromJsonDict(
            raw_ir)  # type: reports_4_0_0.CancerInterpretationRequest
        try:
            ir_migrated, ir_round_tripped = self.migration_runner.roundtrip_cancer_ir(ir, case.assembly)
        except MigrationError as e:
            logging.error("Skipping case {}-{}: {}".format(case_id, version, e.message))
            return
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

        if not is_valid:
            logging.error("Invalid cancer IR {}-{}".format(case_id, version))
        if not is_valid_round_tripped:
            logging.error("Invalid round tripped cancer IR {}-{}".format(case_id, version))
        logging.error("{} cancer IR {}-{}".format("KO" if differ else "OK", case_id, version))

        # interpreted genome
        if case.has_interpreted_genome():
            ig = reports_4_0_0.CancerInterpretedGenome.fromJsonDict(
                case.raw_interpreted_genome)  # type: reports_4_0_0.CancerInterpretedGenome
            ig_migrated, ig_round_tripped = self.migration_runner.roundtrip_cancer_ig(ig, case.assembly)
            is_valid = ig_migrated.validate(reports_6_0_0.InterpretedGenome, ig_migrated.toJsonDict())
            is_valid_round_tripped = ig_round_tripped.validate(
                reports_4_0_0.CancerInterpretedGenome, ig_round_tripped.toJsonDict())
            differ = self.migration_runner.diff_round_tripped(
                ig, ig_round_tripped, ignore_fields=["analysisId", "additionalTextualVariantAnnotations", "commonAf"])
            differ |= self._check_actions(ig.reportedVariants, ig_round_tripped.reportedVariants)
            if not is_valid:
                logging.error("Invalid cancer IG {}-{}".format(case_id, version))
            if not is_valid_round_tripped:
                logging.error("Invalid round tripped cancer IG {}-{}".format(case_id, version))
            logging.error("{} cancer IG {}-{}".format("KO" if differ else "OK", case_id, version))

        # clinical report
        if case.has_clinical_report():
            cr = reports_4_0_0.ClinicalReportCancer.fromJsonDict(
                case.raw_clinical_report)  # type: reports_4_0_0.ClinicalReportCancer
            cr_migrated, cr_round_tripped = self.migration_runner.roundtrip_cancer_cr(cr, case.assembly)
            is_valid = cr_migrated.validate(reports_6_0_0.ClinicalReport, cr_migrated.toJsonDict())
            is_valid_round_tripped = cr_round_tripped.validate(
                reports_4_0_0.ClinicalReportCancer, cr_round_tripped.toJsonDict())
            differ = self.migration_runner.diff_round_tripped(
                cr, cr_round_tripped, ignore_fields=["analysisId", "additionalTextualVariantAnnotations", "commonAf",
                                                     "genePanelsCoverage", "actions"])
            differ |= self._check_actions(cr.candidateVariants, cr_round_tripped.candidateVariants)
            if not is_valid:
                logging.error("Invalid cancer CR {}-{}".format(case_id, version))
            if not is_valid_round_tripped:
                logging.error("Invalid round tripped cancer CR {}-{}".format(case_id, version))
            logging.error("{} cancer CR {}-{}".format("KO" if differ else "OK", case_id, version))

    def run(self):
        print "Check your results in '{}'".format(self.log_file)
        for case in self.cipapi_client.get_cases(program=Program.cancer):  # type: CipApiCase
            self.process_case(case)


if __name__ == '__main__':
    round_tripper = RealRoundTripperCancer()
    round_tripper.run()

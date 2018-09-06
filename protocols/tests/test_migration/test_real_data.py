from pycipapi.cipapi_client import CipApiClient, CipApiCase
import getpass
from protocols.reports_6_0_0 import Program
from protocols.reports_4_0_0 import CancerInterpretationRequest, CancerInterpretedGenome, ClinicalReportCancer
from protocols.tests.test_migration.migration_runner import MigrationRunner
import logging
import os


# configures logging to get only logs about the failed cases
log_file = "real_data.log"
os.remove(log_file)
logging.basicConfig(level=logging.ERROR, filename="real_data.log")
gel_user = raw_input("User:")
gel_password = getpass.getpass("Password:")
cipapi_client = CipApiClient("https://cipapi-prod.gel.zone", user=gel_user, password=gel_password, retries=-1)
migration_runner = MigrationRunner()

for case in cipapi_client.get_cases(program=Program.cancer):  # type: CipApiCase
    # interpretation request
    raw_ir, _id, version = case._get_raw_interpretation_request()
    ir = CancerInterpretationRequest.fromJsonDict(raw_ir)
    ir_migrated, ir_round_tripped = migration_runner.roundtrip_cancer_ir(ir, case.assembly)
    differ = migration_runner.diff_round_tripped(ir, ir_round_tripped,
                                                 ignore_fields=["analysisUri", "analysisVersion", "TNMStageVersion",
                                                                "TNMStageGrouping",
                                                                "additionalTextualVariantAnnotations",
                                                                "matchedSamples", "commonAf", "actions"])
    logging.error("{} cancer IR id={} version={}".format("KO" if differ else "OK", _id, version))

    # interpreted genome
    if case.has_interpreted_genome():
        ig = CancerInterpretedGenome.fromJsonDict(case.raw_interpreted_genome)
        ig_migrated, ig_round_tripped = migration_runner.roundtrip_cancer_ig(ig, case.assembly)
        differ = migration_runner.diff_round_tripped(ig, ig_round_tripped,
                                                     ignore_fields=["analysisId", "additionalTextualVariantAnnotations",
                                                                    "commonAf"])
        logging.error("{} cancer IG id={} version={}".format("KO" if differ else "OK", _id, version))

    # clinical report
    if case.has_clinical_report():
        cr = ClinicalReportCancer.fromJsonDict(case.raw_clinical_report)
        cr_migrated, cr_round_tripped = migration_runner.roundtrip_cancer_cr(cr, case.assembly)
        differ = migration_runner.diff_round_tripped(cr, cr_round_tripped,
                                                     ignore_fields=["analysisId", "additionalTextualVariantAnnotations",
                                                                    "commonAf", "genePanelsCoverage", "actions"])
        logging.error("{} cancer EQ id={} version={}".format("KO" if differ else "OK", _id, version))

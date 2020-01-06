import logging
import getpass
import abc
import os.path
import json
import threading
import glob
import re
from pycipapi.cipapi_client import CipApiClient, CipApiCase

from protocols.reports_6_0_0 import Assembly
from protocols.tests.test_migration.migration_runner import MigrationRunner


class AbstractRealRoundTripper(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, log_file,  program, data_folder=None, use_data=False):
        # configures logging to get only logs about the failed cases
        self.log_file = log_file
        self.program = program
        self.data_folder = data_folder
        self.use_data = use_data
        logging.basicConfig(filename=self.log_file, level=logging.ERROR,
                            format='%(asctime)s.%(msecs)03d\t%(message)s',
                            datefmt='%H:%M:%S' ,)
        if not use_data:
            gel_user = raw_input("User:")
            gel_password = getpass.getpass("Password:")
            cipapi_url = raw_input("URL:")
            self.cipapi_client = CipApiClient(cipapi_url, user=gel_user, password=gel_password, retries=-1)
        self.migration_runner = MigrationRunner()

    @staticmethod
    def log(status, _type, model_version, case_id, version, *args):
        message = "{status}\t{type}\t{model_version}\t{case_id}-{version}\t0".format(
            status=status, type=_type, model_version=model_version, case_id=case_id, version=version)
        message = "\t".join([message] + list(args))
        logging.error(message)

    @staticmethod
    def log_case(_type, case_id, version, model_version, differ, is_valid, is_valid_round_tripped, millis):
        if not is_valid:
            logging.error("INVALID_FORWARD\t{}\t{}\t{}-{}\t{}".format(_type, model_version, case_id, version, millis))
        if not is_valid_round_tripped:
            logging.error("INVALID_BACKWARD\t{}\t{}\t{}-{}\t{}".format(_type, model_version, case_id, version, millis))
        logging.error("{}\t{}\t{}\t{}-{}\t{}".format(
            "DIFFER" if differ else "OK", _type, model_version, case_id, version, millis))

    @abc.abstractmethod
    def process_case(self, case):
        return

    @staticmethod
    def save_json(data, filename):
        with open(filename, 'w') as fp:
            json.dump(data, fp)

    @staticmethod
    def save_case(case, program, data_folder):
        raw_ir, case_id, version = case._get_raw_interpretation_request()
        AbstractRealRoundTripper.save_json(
            raw_ir, os.path.join(data_folder, "{program}-{id}-{version}-{type}.json".format(
                program=program, type="IR", id=case_id, version=version)))
        if case.has_interpreted_genome():
            raw_ig = case.raw_interpreted_genome
            AbstractRealRoundTripper.save_json(
                raw_ig, os.path.join(data_folder, "{program}-{id}-{version}-{type}.json".format(
                    program=program, type="IG", id=case_id, version=version)))
        if case.has_clinical_report():
            raw_cr = case.raw_clinical_report
            AbstractRealRoundTripper.save_json(
                raw_cr, os.path.join(data_folder, "{program}-{id}-{version}-{type}.json".format(
                    program=program, type="CR", id=case_id, version=version)))
        if case.has_exit_questionnaire():
            raw_eq = case.raw_questionnaire
            AbstractRealRoundTripper.save_json(
                raw_eq, os.path.join(data_folder, "{program}-{id}-{version}-{type}.json".format(
                    program=program, type="EQ", id=case_id, version=version)))

    def build_case(self, ir_json_name):
        matches = re.search(".*{}-(.*)-(.*)-IR.json".format(self.program), ir_json_name)
        if matches:
            case_id = matches.group(1)
            case_version = matches.group(2)
        else:
            raise ValueError("Failed to read id and version from file name")
        raw_ir = json.load(open(ir_json_name))
        raw_ig = None
        raw_cr = None
        raw_eq = None
        igs = glob.glob(
            os.path.join(self.data_folder, "*-{}-{}-IG.json".format(case_id, case_version)))
        if igs:
            ig_json_name = igs[0]
            raw_ig = json.load(open(ig_json_name))
        crs = glob.glob(
            os.path.join(self.data_folder, "*-{}-{}-CR.json".format(case_id, case_version)))
        if crs:
            cr_json_name = crs[0]
            raw_cr = json.load(open(cr_json_name))
        eqs = glob.glob(
            os.path.join(self.data_folder, "*-{}-{}-EQ.json".format(case_id, case_version)))
        if eqs:
            eq_json_name = eqs[0]
            raw_eq = json.load(open(eq_json_name))
        case = CipApiCase(case_id, case_version, self.program, Assembly.GRCh38, raw_ir, raw_ig, raw_cr, raw_eq)
        return case

    def run(self):
        print "Check your results in '{}'".format(self.log_file)
        if self.use_data:
            def patched_init(self, case_id, version, program, assembly, raw_ir, raw_ig, raw_cr, raw_eq):
                self.assembly = assembly
                self.program = program
                self.case_id = case_id
                self.case_version = version
                self.raw_interpretation_request = raw_ir
                self.raw_interpreted_genome = raw_ig
                self.raw_clinical_report = raw_cr
                self.raw_questionnaire = raw_eq
            CipApiCase.__init__ = patched_init
            for ir_json_name in glob.glob(os.path.join(self.data_folder, "{}-*-IR.json".format(self.program))):
                case = self.build_case(ir_json_name)
                self.process_case(case)
        else:
            for case in self.cipapi_client.get_cases(program=self.program):  # type: CipApiCase
                self.process_case(case)
                if self.data_folder:
                    save_thread = threading.Thread(target=AbstractRealRoundTripper.save_case, args=(case, self.program, self.data_folder))
                    save_thread.start()

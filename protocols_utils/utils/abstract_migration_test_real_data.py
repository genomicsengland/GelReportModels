import logging
import getpass
import abc
import os.path
import ujson as json
import threading
from pycipapi.cipapi_client import CipApiClient, CipApiCase
from protocols.tests.test_migration.migration_runner import MigrationRunner


class AbstractRealRoundTripper(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, log_file,  program, data_folder=None):
        # configures logging to get only logs about the failed cases
        self.log_file = log_file
        self.program = program
        self.data_folder = data_folder
        logging.basicConfig(filename=self.log_file, level=logging.ERROR,
                            format='%(asctime)s.%(msecs)03d\t%(message)s',
                            datefmt='%H:%M:%S' ,)
        gel_user = raw_input("User:")
        gel_password = getpass.getpass("Password:")
        cipapi_url = raw_input("URL:")
        self.cipapi_client = CipApiClient(cipapi_url, user=gel_user, password=gel_password, retries=-1)
        self.migration_runner = MigrationRunner()

    @staticmethod
    def log(status, _type, model_version, case_id, version, *args):
        message = "{status}\t{type}\t{model_version}\t{case_id}-{version}".format(
            status=status, type=_type, model_version=model_version, case_id=case_id, version=version)
        message = "\t".join([message] + list(args))
        logging.error(message)

    @staticmethod
    def log_case(_type, case_id, version, model_version, differ, is_valid, is_valid_round_tripped):
        if not is_valid:
            logging.error("INVALID_FORWARD\t{}\t{}\t{}-{}".format(_type, model_version, case_id, version))
        if not is_valid_round_tripped:
            logging.error("INVALID_BACKWARD\t{}\t{}\t{}-{}".format(_type, model_version, case_id, version))
        logging.error("{}\t{}\t{}\t{}-{}".format("DIFFER" if differ else "OK", _type, model_version, case_id, version))

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
            raw_ir, os.path.join(data_folder, "{program}-{type}-{id}-{version}.json".format(
                program=program, type="IR", id=case_id, version=version)))
        if case.has_interpreted_genome():
            raw_ig = case.raw_interpreted_genome
            AbstractRealRoundTripper.save_json(
                raw_ig, os.path.join(data_folder, "{program}-{type}-{id}-{version}.json".format(
                    program=program, type="IG", id=case_id, version=version)))
        if case.has_clinical_report():
            raw_cr = case.raw_clinical_report
            AbstractRealRoundTripper.save_json(
                raw_cr, os.path.join(data_folder, "{program}-{type}-{id}-{version}.json".format(
                    program=program, type="CR", id=case_id, version=version)))
        if case.has_exit_questionnaire():
            raw_eq = case.raw_questionnaire
            AbstractRealRoundTripper.save_json(
                raw_eq, os.path.join(data_folder, "{program}-{type}-{id}-{version}.json".format(
                    program=program, type="EQ", id=case_id, version=version)))

    def run(self):
        print "Check your results in '{}'".format(self.log_file)
        for case in self.cipapi_client.get_cases(program=self.program):  # type: CipApiCase
            self.process_case(case)
            if self.data_folder:
                save_thread = threading.Thread(target=AbstractRealRoundTripper.save_case, args=(case, self.program, self.data_folder))
                save_thread.start()
                # AbstractRealRoundTripper.save_case(case, self.program, self.data_folder)

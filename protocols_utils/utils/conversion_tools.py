#!/usr/bin/env python
from __future__ import print_function
import argparse
import fnmatch
import os
import os.path
import sys
import subprocess
import logging
import errno
from protocols_utils.code_generation.process_schemas import SchemaGenerator, ProtocolGenerator

logging.basicConfig(level=logging.DEBUG)
BASE_DIR = os.path.dirname(__file__)
AVRO_TOOLS_JAR = os.path.join(BASE_DIR, "../..", "resources/bin", "avro-tools-1.7.7.jar")
GA4GH_CODE_GENERATION = os.path.join(BASE_DIR, "code_generation", "process_schemas.py")
IDL_EXTENSION = "avdl"
JSON_EXTENSION = "avsc"
AVPR_EXTENSION = "avpr"
HTML_EXTENSION = "html"


def run_command(command, fail_if_error=True, cwd=None):
    """
    Runs a given command
    :param cwd:
    :param fail_if_error:
    :param command:
    :return:
    """
    if cwd is not None:
        sp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    else:
        sp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = sp.communicate()
    if stdout is not None and stdout != "":
        logging.info(stdout)
    if stderr is not None and stderr != "":
        logging.error(stderr)
    # raise an error if sort return code is other than 0
    if sp.returncode:
        error_message = 'Command [{0}] returned error code [{1}]'.format(command, str(sp.returncode))
        logging.error(error_message)
        if fail_if_error:
            raise ValueError(error_message)


def makedir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class ConversionTools(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='GEL models toolbox',
            usage='''conversion_tools.py <command> [<args>]''')
        parser.add_argument(
            'command',
            help='Subcommand to run (idl2json|idl2avpr|json2java|idl2python|json2python|avpr2html|update_docs_index|buildVersionPackage)'
        )
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def idl2json(self):
        """
        Transform all IDL files in input folder to AVRO schemas in the output folder
        :return:
        """
        parser = argparse.ArgumentParser(
            description='Converts IDL to Avro JSON schema')
        # prefixing the argument with -- means it's optional
        parser.add_argument('--input', help='Input folder containing *.avdl files')
        parser.add_argument('--output', help='Output folder for the JSON schemas')
        args = parser.parse_args(sys.argv[2:])
        logging.info('idl2schema')
        makedir(args.output)
        idls = [os.path.join(dirpath, f)
                for dirpath, dirnames, files in os.walk(args.input)
                for f in fnmatch.filter(files, "*.{}".format(IDL_EXTENSION))]

        for idl in idls:
            logging.info("Transforming: " + idl)
            idl2schemata_command = "java -jar {} idl2schemata {} {}".format(
                AVRO_TOOLS_JAR, idl, args.output
            )
            logging.info("Running: [%s]" % idl2schemata_command)
            run_command(idl2schemata_command)

    def idl2avpr(self):
        """
        Transform all IDL files in input folder to AVPRs in the output folder
        :return:
        """
        parser = argparse.ArgumentParser(
            description='Converts IDL to AVPR')
        # prefixing the argument with -- means it's optional
        parser.add_argument('--input', help='Input folder containing *.avdl files')
        parser.add_argument('--output', help='Output folder for the AVPRs')
        args = parser.parse_args(sys.argv[2:])
        logging.info('idl2avpr')
        makedir(args.output)
        idls = [os.path.join(dirpath, f)
                for dirpath, dirnames, files in os.walk(args.input)
                for f in fnmatch.filter(files, "*.{}".format(IDL_EXTENSION))]
        for idl in idls:
            logging.info("Transforming: " + idl)
            file_name = os.path.basename(idl).replace(IDL_EXTENSION, AVPR_EXTENSION)
            idl2avpr_command = "java -jar {} idl {} {}/{}".format(
                AVRO_TOOLS_JAR, idl, args.output, file_name
            )
            logging.info("Running: [%s]" % idl2avpr_command)
            run_command(idl2avpr_command)


    def json2java(self):
        """
        Transform all JSON Avro schemas in a given folder to Java source code.
        :return:
        """
        parser = argparse.ArgumentParser(
            description='Generates Java source code from Avro schemas')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('--input', help='Input folder containing *.avdl files')
        parser.add_argument('--output', help='Output folder for the Java source code')
        args = parser.parse_args(sys.argv[2:])
        logging.info('json2java')
        makedir(args.output)
        jsons = [os.path.join(dirpath, f)
                for dirpath, dirnames, files in os.walk(args.input)
                for f in fnmatch.filter(files, "*.{}".format(JSON_EXTENSION))]
        for json in jsons:
            logging.info("Transforming: " + json)
            idl2avpr_command = "java -jar {} compile -string schema {} {}".format(
                AVRO_TOOLS_JAR, json, args.output
            )
            logging.info("Running: [%s]" % idl2avpr_command)
            run_command(idl2avpr_command)

    def idl2python(self):
        """
        Transforms all IDL Avro schemas in a given folder to Python source code.
        :return:
        """
        parser = argparse.ArgumentParser(
            description='Generates Python source code from Avro IDLs')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('--input', help='Input folder containing *.avdl files')
        parser.add_argument('--output-file', help='Output file for the Python source code')
        parser.add_argument('--version', help='Python package version')
        args = parser.parse_args(sys.argv[2:])
        logging.info('idl2python')
        makedir(os.path.dirname(args.output))
        idl2python_command = "python {} --inputSchemasDirectory {} --avro-tools-jar {} --outputFile {} {} --verbose".format(
            GA4GH_CODE_GENERATION, args.input, AVRO_TOOLS_JAR, args.output_file, args.version
        )
        logging.info("Running: [%s]" % idl2python_command)
        run_command(idl2python_command)

    @staticmethod
    def json2python():
        """
        Transforms all IDL JSON schemas in a given folder to Python source code.
        :return:
        """
        parser = argparse.ArgumentParser(
            description='Generates Python source code from Avro JSON schemas')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('--input', help='Input folder containing *.avsc files')
        parser.add_argument('--output-file', help='Output file for the Python source code (e.g.: reports_4.1.0.py)')
        parser.add_argument('--version', help='Python package version')
        args = parser.parse_args(sys.argv[2:])
        logging.info('json2python')
        logging.info(args)
        makedir(os.path.dirname(args.output_file))
        sg = SchemaGenerator(args.version, args.input, args.output_file, True)
        sg.write()

    @staticmethod
    def buildVersionPackage():
        parser = argparse.ArgumentParser(
            description='Generates Python source code from Avro JSON schemas')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('--builds-file', help='Input folder containing *.avsc files')
        parser.add_argument('--output-dir', help='Output file for the Python source code (e.g.: protocol_7.1.py)')
        parser.add_argument('--version', help='Build package version')
        args = parser.parse_args(sys.argv[2:])

        logging.info('build protocol')
        logging.info(args)

        makedir(args.output_dir)

        pg = ProtocolGenerator(args.builds_file, args.output_dir, args.version)
        pg.write()

    @staticmethod
    def avpr2html():
        """
        Transforms all AVPR schemas in a given folder to HTML documentation.
        :return:
        """
        parser = argparse.ArgumentParser(
            description='Generates HTML documentation from Avro AVPR')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('--input-file', help='Input AVPR file')
        parser.add_argument('--output', help='Output folder for the HTML documentation')
        args = parser.parse_args(sys.argv[2:])
        logging.info('avpr2html')
        makedir(args.output)
        output_html = os.path.basename(args.input_file).replace(AVPR_EXTENSION, HTML_EXTENSION)
        avrodoc_command = "avrodoc {} > {}".format(args.input_file, os.path.join(args.output, output_html))
        logging.info("Running: [%s]" % avrodoc_command)
        run_command(avrodoc_command)

    @staticmethod
    def update_docs_index():
        """
        Transforms all AVPR schemas in a given folder to HTML documentation.
        :return:
        """
        parser = argparse.ArgumentParser(
            description='Updates documentation index')
        # NOT prefixing the argument with -- means it's not optional
        args = parser.parse_args(sys.argv[2:])
        logging.info('Updating docs index...')
        sphinx_command = "make html"
        logging.info("Running: [%s]" % sphinx_command)
        run_command(sphinx_command, cwd="./docs")


if __name__ == '__main__':
    ConversionTools()

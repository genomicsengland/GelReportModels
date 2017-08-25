import json
import os
import sys
import fnmatch
import logging
import shutil
import subprocess

import argparse

__author__ = 'antonior'

logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(__file__)
AVRO_TOOLS_JAR = os.path.join(BASE_DIR, "resources", "bin", "avro-tools-1.7.7.jar")
MODEL_SHORT_NAME = {
    'org.ga4gh.models': 'ga4gh',
    'org.gel.models.cva.avro': 'cva',
    'org.gel.models.metrics.avro': 'metrics',
    'org.gel.models.participant.avro': 'participant',
    'org.gel.models.report.avro': 'reports',
    'org.opencb.biodata.models': 'opencb'
}

class GelReportModelsError(Exception):
    """
    A exception to raise when an error sorting happens
    """
    pass

def run_command(command, fail_if_error=True):
    """

    :param command:
    :return:
    """
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
            raise GelReportModelsError(error_message)

def create_folder(folder):
    """

    :param folder:
    :return:
    """
    if not os.path.exists(folder):
        run_command('mkdir -p ' + folder)

def create_other_schemas(idls_folder, json_folder, avrp_folder):
    """

    :param idls_folder:
    :param json_folder:
    :param avrp_folder:
    :return:
    """
    idls = [os.path.join(dirpath, f)
            for dirpath, dirnames, files in os.walk(idls_folder)
            for f in fnmatch.filter(files, '*.avdl')]

    logging.info("Transforming AVDL schema to other representations...")
    for idl in idls:
        logging.info("Transforming: " + idl)
        base = os.path.basename(idl).replace(".avdl", "")
        idl2schemata_command = "java -jar " + AVRO_TOOLS_JAR + " idl2schemata " + idl + " " + \
                               os.path.join(json_folder, base)
        logging.info("Running: [%s]" % idl2schemata_command)
        run_command(idl2schemata_command)
        idl_command = "java -jar " + AVRO_TOOLS_JAR + " idl " + idl + " " + os.path.join(avrp_folder, base + ".avpr")
        logging.info("Running: [%s]" % idl_command)
        run_command(idl_command)

def generate_python_sources(schema, source, version):
    """
    Generating Python source code from an AVRO schema
    :param schema: the avro schema
    :param source: the source to be generated
    :param version: the version
    :return:
    """
    logging.info("Version: " + version)
    # GeL models Python source generation
    source_generation_command = "python " + os.path.join(BASE_DIR, "resources", "CodeGenerationFromGA4GH",
                                                         "process_schemas.py --outputFile "
                                                         + source + " --avro-tools-jar " + AVRO_TOOLS_JAR +
                                                         " --inputSchemasDirectory "
                                                         + schema + " " + version + " --verbose    ")
    logging.info(source_generation_command)
    run_command(source_generation_command)
    # copies the source code to the same location without version suffix to act as the latest

def generate_documentation(class_name, avpr_folder, html_folder):
    """
    Generates the documentation for a given class.
    PRE: {class_name}.avpr must exist and a have a correct AVPR format
    :param class_name:
    :param avpr_folder:
    :param html_folder:
    :return:
    """
    avpr_file = "%s.avpr" % class_name
    avrodoc_command = "avrodoc " + os.path.join(avpr_folder, avpr_file) + " > " \
                      + os.path.join(html_folder, "%s.html" % class_name)
    logging.info("Running: [%s]" % avrodoc_command)
    run_command(avrodoc_command)

def build_directories(models_package, models_version):
    return dict(
        idl_folder=os.path.join(BASE_DIR, "schemas", "IDLs", models_package, models_version),
        json_folder=os.path.join(BASE_DIR, "schemas", "JSONs", models_package, models_version),
        avrp_folder= os.path.join(BASE_DIR, "schemas", "AVPRs", models_package, models_version),
        html_folder= os.path.join(BASE_DIR, "docs", "html_schemas", models_package, models_version)
    )


def generated_python_classes(package_name, models_version, idl_folder):
    module_version = models_version.replace('.', '_').replace('-', '_')
    logging.info("Generating Python source code for " + package_name)
    outfile_with_version = os.path.join(BASE_DIR, "protocols",
                                        "{shortname}_{version}.py".format(shortname=MODEL_SHORT_NAME[package_name], version=module_version))
    outfile = os.path.join(BASE_DIR, "protocols", "{shortname}.py".format(shortname=MODEL_SHORT_NAME[package_name]))
    generate_python_sources(idl_folder, outfile_with_version, module_version)
    shutil.copyfile(outfile_with_version, outfile)


def generate_all_doc(avpr_folder, html_folder):
    """
    Search for all *.avpr in the avpr_folder and creates HTML documentation for it
    :param avpr_folder:
    :param html_folder:
    :return:
    """
    for file in os.listdir(avpr_folder):
        if file.endswith('.avpr'):
            generate_documentation(file.replace('.avpr', ''), avpr_folder, html_folder)

def build(models, skip_doc):
    models_dict = {}
    for model in models:
        model_package = model[0]
        model_version = model[1]
        if model_package in models_dict:
            models_dict[model_package].append(model_version)
        else:
            models_dict[model_package] = [model_version]
        folders = build_directories(model_package, model_version)
        for folder in folders:
            create_folder(folders[folder])
        create_other_schemas(idls_folder=folders['idl_folder'], json_folder=folders['json_folder'],
                             avrp_folder=folders['avrp_folder']
                             )
        generated_python_classes(package_name=model_package, models_version=model_version, idl_folder=folders['idl_folder'])
        if not skip_doc:
            generate_all_doc(avpr_folder=folders['avrp_folder'], html_folder=folders['html_folder'])
    generate_rst_index(models_dict)

def generate_rst_index(models):
    """
    Overwrites existing file at docs/source/models.rst
    :param models:
    :return:
    """
    body = []
    references = []
    # adds title
    title = "GEL Models documentation"
    body.append(title)
    body.append("=" * len(title))
    for package in models:
        model_package = package
        # adds a section for a package
        body.append("")
        body.append(model_package)
        body.append("-" * len(model_package))
        body.append("")
        model_versions = models[package]
        for version in model_versions:
            # adds a subsection for a version
            body.append("")
            body.append(version)
            body.append("^" * len(version))
            body.append("")
            docs_folder = os.path.join(BASE_DIR, "docs", "html_schemas", package, version)
            htmls = [f.replace(".html", "") for _, _, files in os.walk(docs_folder)
                    for f in fnmatch.filter(files, '*.html')]
            for html in htmls:
                # adds an entry to a class
                element_id = "{package}.{version}.{clazz}".format(
                    package=package, version=version, clazz=html
                ).replace(".", "").replace("-", "")
                body.append(
                    "* |{element_id}|".format(
                        element_id=element_id
                    )
                )
                # adds a link to a class
                references.append(".. |{element_id}| raw:: html"
                                  .format(element_id=element_id)
                                  )
                references.append("")
                references.append(
                    "    <a href=\"html_schemas/{package}/{version}/{clazz}.html\" target=\"_blank\">{clazz}</a>"
                        .format(package=package, version=version, clazz=html)
                )
    with open(os.path.join(BASE_DIR, "docs", "source", "models.rst"), 'w+') as f:
        for line in body:
            f.write(line + '\n')
        f.write('\n')
        for line in references:
            f.write(line + '\n')


def main():
    parser = argparse.ArgumentParser(
        description='Generate AVPR, JSON, HTML, PYTHON Classes and JAVA Classes from the idls models')
    parser.add_argument(
        '--models',
        metavar='models and version',
        nargs='+',
        default=[
            'org.gel.models.participant.avro::1.0.0', 'org.gel.models.participant.avro::1.0.1',
            'org.gel.models.participant.avro::1.0.3',
            'org.gel.models.participant.avro::1.0.4-SNAPSHOT',
            'org.gel.models.metrics.avro::1.0.0', 'org.gel.models.metrics.avro::1.0.1',
            'org.gel.models.metrics.avro::1.1.0-SNAPSHOT',
            'org.ga4gh.models::3.0.0', 'org.ga4gh.models::3.1.0-SNAPSHOT',
            'org.gel.models.report.avro::2.1.0', 'org.gel.models.report.avro::3.0.0',
            'org.gel.models.report.avro::3.1.0', 'org.gel.models.report.avro::4.0.0',
            'org.gel.models.report.avro::4.1.0', 'org.gel.models.report.avro::4.2.0-SNAPSHOT',
            'org.gel.models.cva.avro::0.3.1', 'org.gel.models.cva.avro::0.4.0-SNAPSHOT',
            'org.opencb.biodata.models::1.2.0'
        ],
        help='List of models packages and versions to generated, in the following format package::version'
    )
    parser.add_argument('--skip_doc', default=False, action='store_true', help='Documentation will be skipped')
    args = parser.parse_args()

    list_of_models = []
    for model in args.models:
        print model
        model, version = model.split('::')
        if not model or not version:
            logging.error('Please provide the version and the name of the package in the following format: package::version')
            sys.exit(-1)
        if model not in MODEL_SHORT_NAME:

            logging.error(str(model) + 'is not a valid package name')
            sys.exit(-1)

        list_of_models.append((model, version))

    build(models=list_of_models, skip_doc=args.skip_doc)


if __name__ == '__main__':
    main()

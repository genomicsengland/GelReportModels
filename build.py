import json
import os
import sys
import fnmatch
import logging
import shutil

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
#TODO: handle this at the version level
MODEL_DOCUMENTATION = {
    'org.gel.models.report.avro': [
        "ClinicalReportRD",
        "ClinicalReportCancer",
        "InterpretationRequestRD",
        "InterpretationRequestCancer",
        "InterpretedGenomesRD",
        "InterpretedGenomesCancer",
        "AuditLog",
        "MDTDeliveryProtocol",
        "ExitQuestionnaire"
    ],
    'org.gel.models.cva.avro':[
        "EvidenceSet",
        "Comment",
        "ReportedVariant",
        "ObservedVariant",
        "DataIntake"
    ],
    'org.opencb.biodata.models':[
        "evidence",
        "read",
        "variant",
        "variantAnnotation",

    ],
    'org.ga4gh.models':[
        "common",
        "metadata",
        "methods",
        "readmethods",
        "reads",
        "referencemethods",
        "references",
        "variantmethods",
        "variants",
    ],
    'org.gel.models.participant.avro':[
        "RDParticipant",
        "CancerParticipant",
        "RDParticipantChangeLog",
        "CommonParticipant",
        "ParticipantSensitiveInformation",
        "VersionControl"
    ],
    'org.gel.models.metrics.avro':[
        "GelBamMetrics",
        "GelVcfMetrics",
        "individualState",
        "RareDiseaseInterpretationPipeline",
        "sampleState",
        "SupplementaryAnalysisResults"
    ]
}


def create_folder(folder):
    """

    :param folder:
    :return:
    """
    if not os.path.exists(folder):
        os.system('mkdir -p ' + folder)

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
        os.system(idl2schemata_command)
        idl_command = "java -jar " + AVRO_TOOLS_JAR + " idl " + idl + " " + os.path.join(avrp_folder, base + ".avpr")
        logging.info("Running: [%s]" % idl_command)
        os.system(idl_command)

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
    os.system(source_generation_command)
    # copies the source code to the same location without version suffix to act as the latest


def generate_documentation(class_name, avrp_folder, html_folder):
    """

    :param class_name:
    :param avrp_folder:
    :param html_folder:
    :return:
    """
    avrodoc_command = "avrodoc " + os.path.join(avrp_folder, "%s.avpr" % class_name) + " > " \
                      + os.path.join(html_folder, "%s.html" % class_name)
    logging.info("Running: [%s]" % avrodoc_command)
    os.system(avrodoc_command)

def build_directories(models_package, models_version):
    return dict(
        idl_folder=os.path.join(BASE_DIR, "schemas", "IDLs", models_package, models_version),
        json_folder=os.path.join(BASE_DIR, "schemas", "JSONs", models_package, models_version),
        avrp_folder= os.path.join(BASE_DIR, "schemas", "AVPRs", models_package, models_version),
        html_folder= os.path.join(BASE_DIR, "docs", "html_schemas", models_package, models_version)
    )


def generated_python_classes(package_name, models_version, idl_folder):
    module_version = models_version.replace('.', '_')
    logging.info("Generating Python source code for " + package_name)
    outfile_with_version = os.path.join(BASE_DIR, "protocols",
                                        "{shortname}_{version}.py".format(shortname=MODEL_SHORT_NAME[package_name], version=module_version))
    outfile = os.path.join(BASE_DIR, "protocols", "{shortname}.py".format(shortname=MODEL_SHORT_NAME[package_name]))
    generate_python_sources(idl_folder, outfile_with_version, models_version)
    shutil.copyfile(outfile_with_version, outfile)


def generate_all_doc(package_name, avrp_folder, html_folder):
    if package_name in MODEL_DOCUMENTATION:
        for model in MODEL_DOCUMENTATION[package_name]:
            generate_documentation(model, avrp_folder, html_folder)

def build(models, skip_doc):
    for model in models:
        model_package = model[0]
        model_version = model[1]
        folders = build_directories(model_package, model_version)
        for folder in folders:
            create_folder(folders[folder])
        create_other_schemas(idls_folder=folders['idl_folder'], json_folder=folders['json_folder'],
                             avrp_folder=folders['avrp_folder']
                             )
        generated_python_classes(package_name=model_package, models_version=model_version, idl_folder=folders['idl_folder'])
        if not skip_doc:
            generate_all_doc(package_name=model_package, avrp_folder=folders['avrp_folder'], html_folder=folders['html_folder'])

def main():
    parser = argparse.ArgumentParser(
        description='Generate AVPR, JSON, HTML, PYTHON Classes and JAVA Classes from the idls models')
    parser.add_argument(
        '--models',
        metavar='models and version',
        nargs='+',
        default=[
            'org.gel.models.participant.avro::1.0.0', 'org.gel.models.participant.avro::1.0.1',
            'org.gel.models.participant.avro::1.0.2',
            'org.gel.models.metrics.avro::1.0.0', 'org.gel.models.metrics.avro::1.0.1',
            'org.ga4gh.models::3.0.0',
            'org.gel.models.report.avro::2.1.0', 'org.gel.models.report.avro::3.0.0',
            'org.gel.models.report.avro::3.1.0', 'org.gel.models.report.avro::4.0.0',
            'org.gel.models.cva.avro::0.3.1', 'org.opencb.biodata.models::1.2.0-SNAPSHOT'
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

import json
import os
import sys
import fnmatch
import logging

__author__ = 'antonior'

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


logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(__file__)
AVRO_TOOLS_JAR = os.path.join(BASE_DIR, "resources", "bin", "avro-tools-1.7.7.jar")

if len(sys.argv) == 9:
    report_package_version = sys.argv[1]
    report_models_version = sys.argv[2]
    ga4gh_package_version = sys.argv[3]
    ga4gh_models_version = sys.argv[4]
    cva_package_version = sys.argv[5]
    cva_models_version = sys.argv[6]
    opencb_package_version = sys.argv[7]
    opencb_models_version = sys.argv[8]
else:
    logging.error("Please, provide a version for the models")
    sys.exit(-1)

report_module_version = report_models_version.replace('.', '_')
ga4gh_module_version = ga4gh_models_version.replace('.', '_')
cva_module_version = cva_models_version.replace('.', '_')
opencb_module_version = opencb_models_version.replace('.', '_')

report_idl_folder = os.path.join(BASE_DIR, "schemas", "IDLs", report_package_version, report_models_version)
report_json_folder = os.path.join(BASE_DIR, "schemas", "JSONs", report_package_version, report_models_version)
report_avrp_folder = os.path.join(BASE_DIR, "schemas", "AVPRs", report_package_version, report_models_version)
report_html_folder = os.path.join(BASE_DIR, "docs", "html_schemas", report_package_version, report_models_version)
ga4gh_idl_folder = os.path.join(BASE_DIR, "schemas", "IDLs", ga4gh_package_version, ga4gh_models_version)
ga4gh_json_folder = os.path.join(BASE_DIR, "schemas", "JSONs", ga4gh_package_version, ga4gh_models_version)
ga4gh_avrp_folder = os.path.join(BASE_DIR, "schemas", "AVPRs", ga4gh_package_version, ga4gh_models_version)
ga4gh_html_folder = os.path.join(BASE_DIR, "docs", "html_schemas", ga4gh_package_version, ga4gh_models_version)
cva_idl_folder = os.path.join(BASE_DIR, "schemas", "IDLs", cva_package_version, cva_models_version)
cva_json_folder = os.path.join(BASE_DIR, "schemas", "JSONs", cva_package_version, cva_models_version)
cva_avrp_folder = os.path.join(BASE_DIR, "schemas", "AVPRs", cva_package_version, cva_models_version)
cva_html_folder = os.path.join(BASE_DIR, "docs", "html_schemas", cva_package_version, cva_models_version)
opencb_idl_folder = os.path.join(BASE_DIR, "schemas", "IDLs", opencb_package_version, opencb_models_version)
opencb_json_folder = os.path.join(BASE_DIR, "schemas", "JSONs", opencb_package_version, opencb_models_version)
opencb_avrp_folder = os.path.join(BASE_DIR, "schemas", "AVPRs", opencb_package_version, opencb_models_version)
opencb_html_folder = os.path.join(BASE_DIR, "docs", "html_schemas", opencb_package_version, opencb_models_version)

folders2create = [report_json_folder, report_avrp_folder, report_html_folder,
                  ga4gh_json_folder, ga4gh_avrp_folder, ga4gh_html_folder,
                  cva_json_folder, cva_avrp_folder, cva_html_folder,
                  opencb_json_folder, opencb_avrp_folder, opencb_html_folder]
for folder in folders2create:
    create_folder(folder)


create_other_schemas(report_idl_folder, report_json_folder, report_avrp_folder)
create_other_schemas(ga4gh_idl_folder, ga4gh_json_folder, ga4gh_avrp_folder)
create_other_schemas(cva_idl_folder, cva_json_folder, cva_avrp_folder)
create_other_schemas(opencb_idl_folder, opencb_json_folder, opencb_avrp_folder)


logging.info("Generating Python source code from schemas...")
outfile = os.path.join(BASE_DIR, "protocols", "GelProtocols_{version}.py".format(version=report_module_version))
ga4gh_outfile = os.path.join(BASE_DIR, "protocols", "GA4GHProtocols_{version}.py".format(version=ga4gh_module_version))
openCB_outfile = os.path.join(BASE_DIR, "protocols", "openCBProtocols_{version}.py".format(version=opencb_module_version))
cva_outfile = os.path.join(BASE_DIR, "protocols", "CVAProtocols_{version}.py".format(version=cva_module_version))

version = json.load(open(os.path.join(report_json_folder, "VersionControl", "VersionControl.avsc")))["fields"][0]["default"]
logging.info("Version: " + version)
# GeL models Python source generation
generate_python_sources(report_idl_folder, outfile, version)
# GA4GH models Python source generation
generate_python_sources(ga4gh_idl_folder, ga4gh_outfile, version)
# OpenCB models Python source generation
generate_python_sources(opencb_idl_folder, openCB_outfile, version)
# CVA models Python source generation
generate_python_sources(cva_idl_folder, cva_outfile, version)


# Builds models documentation
## reporting
generate_documentation("RDParticipant", report_avrp_folder, report_html_folder)
generate_documentation("ClinicalReportRD", report_avrp_folder, report_html_folder)
generate_documentation("ClinicalReportCancer", report_avrp_folder, report_html_folder)
generate_documentation("InterpretationRequestRD", report_avrp_folder, report_html_folder)
generate_documentation("InterpretationRequestCancer", report_avrp_folder, report_html_folder)
generate_documentation("InterpretedGenomesRD", report_avrp_folder, report_html_folder)
generate_documentation("InterpretedGenomesCancer", report_avrp_folder, report_html_folder)
generate_documentation("CancerParticipant", report_avrp_folder, report_html_folder)
generate_documentation("GelBamMetrics", report_avrp_folder, report_html_folder)
generate_documentation("AuditLog", report_avrp_folder, report_html_folder)
generate_documentation("RDParticipantChangeLog", report_avrp_folder, report_html_folder)
generate_documentation("MDTDeliveryProtocol", report_avrp_folder, report_html_folder)
generate_documentation("SupplementaryAnalysisResults", report_avrp_folder, report_html_folder)
generate_documentation("ExitQuestionnaire", report_avrp_folder, report_html_folder)
## CVA
generate_documentation("EvidenceSet", cva_avrp_folder, cva_html_folder)
generate_documentation("Comment", cva_avrp_folder, cva_html_folder)
generate_documentation("ReportEventContainer", cva_avrp_folder, cva_html_folder)
generate_documentation("ObservedVariant", cva_avrp_folder, cva_html_folder)
generate_documentation("DataIntake", cva_avrp_folder, cva_html_folder)
## OpenCB
generate_documentation("evidence", opencb_avrp_folder, opencb_html_folder)
generate_documentation("read", opencb_avrp_folder, opencb_html_folder)
generate_documentation("variant", opencb_avrp_folder, opencb_html_folder)
generate_documentation("variantAnnotation", opencb_avrp_folder, opencb_html_folder)
## GA4GH
generate_documentation("common", ga4gh_avrp_folder, ga4gh_html_folder)
generate_documentation("metadata", ga4gh_avrp_folder, ga4gh_html_folder)
generate_documentation("methods", ga4gh_avrp_folder, ga4gh_html_folder)
generate_documentation("readmethods", ga4gh_avrp_folder, ga4gh_html_folder)
generate_documentation("reads", ga4gh_avrp_folder, ga4gh_html_folder)
generate_documentation("referencemethods", ga4gh_avrp_folder, ga4gh_html_folder)
generate_documentation("references", ga4gh_avrp_folder, ga4gh_html_folder)
generate_documentation("variantmethods", ga4gh_avrp_folder, ga4gh_html_folder)
generate_documentation("variants", ga4gh_avrp_folder, ga4gh_html_folder)
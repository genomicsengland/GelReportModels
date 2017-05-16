import json
import os
import sys
import fnmatch
import logging

__author__ = 'antonior'

logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(__file__)

if len(sys.argv) > 1:
    v = sys.argv[1]
else:
    v = 'latest'

module_version = v.replace('.', '_')

avro_tools_jar = os.path.join(BASE_DIR, "resources", "bin", "avro-tools-1.7.7.jar")
json_folder = os.path.join(BASE_DIR, "schemas", "JSONs", v)
avrp_folder = os.path.join(BASE_DIR, "schemas", "AVPRs", v)
html_folder = os.path.join(BASE_DIR, "docs", "html_schemas", v)

if not os.path.exists(json_folder):
    os.system('mkdir -p ' + json_folder)

if not os.path.exists(avrp_folder):
    os.system('mkdir -p ' + avrp_folder)

if not os.path.exists(html_folder):
    os.system('mkdir -p ' + html_folder)


idl_base_path = os.path.join(BASE_DIR, "schemas", "IDLs", v)
idls = [os.path.join(dirpath, f)
        for dirpath, dirnames, files in os.walk(idl_base_path)
        for f in fnmatch.filter(files, '*.avdl')]

logging.info("Transforming AVDL schema to other representations...")
for idl in idls:
    logging.info("Transforming: " + idl)
    base = os.path.basename(idl).replace(".avdl", "")
    idl2schemata_command = "java -jar " + avro_tools_jar + " idl2schemata " + idl + " " + \
                           os.path.join(json_folder, base)
    logging.info("Running: [%s]" % idl2schemata_command)
    os.system(idl2schemata_command)
    idl_command = "java -jar " + avro_tools_jar + " idl " + idl + " " + os.path.join(avrp_folder, base + ".avpr")
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
                                                  + source + " --avro-tools-jar " + avro_tools_jar +
                                                         " --inputSchemasDirectory "
                                                  + schema + " " + version + " --verbose    ")
    logging.info(source_generation_command)
    os.system(source_generation_command)


logging.info("Generating Python source code from schemas...")
schemas = os.path.join(BASE_DIR, "schemas/IDLs", v, "org.gel.models.report.avro")
ga4gh_schemas = os.path.join(BASE_DIR, "schemas/IDLs", v, "org.ga4gh.models")
openCB_schemas = os.path.join(BASE_DIR, "schemas/IDLs", v, "org.opencb.biodata.models.sequence")
cva_schemas = os.path.join(BASE_DIR, "schemas/IDLs", v, "org.gel.models.cva.avro")
ontologies_schemas = os.path.join(BASE_DIR, "schemas/IDLs", v, "org.gel.models.ontologies")
if v == 'latest':
    outfile = os.path.join(BASE_DIR, "protocols", "GelProtocols.py")
else:
    outfile = os.path.join(BASE_DIR, "protocols", "GelProtocols_{version}.py".format(version=module_version))
ga4gh_outfile = os.path.join(BASE_DIR, "protocols", "GA4GHProtocols.py")
openCB_outfile = os.path.join(BASE_DIR, "protocols", "openCBProtocols.py")
cva_outfile = os.path.join(BASE_DIR, "protocols", "CVAProtocols.py")
ontologies_outfile = os.path.join(BASE_DIR, "protocols", "OntologiesProtocols.py")

version = json.load(open(os.path.join(json_folder, "VersionControl", "VersionControl.avsc")))["fields"][0]["default"]
logging.info("Version: " + version)
# GeL models Python source generation
generate_python_sources(schemas, outfile, version)
# GA4GH models Python source generation
generate_python_sources(ga4gh_schemas, ga4gh_outfile, version)
# OpenCB models Python source generation
generate_python_sources(openCB_schemas, openCB_outfile, version)
# Ontologies models Python source generation
generate_python_sources(ontologies_schemas, ontologies_outfile, version)
# CVA models Python source generation
generate_python_sources(cva_schemas, cva_outfile, version)


def generate_documentation(class_name):
    avrodoc_command = "avrodoc " + os.path.join(avrp_folder, "%s.avpr" % class_name) + " > " + os.path.join(html_folder, "%s.html" % class_name)
    logging.info("Running: [%s]" % avrodoc_command)
    os.system(avrodoc_command)

# Builds models documentation
generate_documentation("RDParticipant")
generate_documentation("ClinicalReportRD")
generate_documentation("ClinicalReportCancer")
generate_documentation("InterpretationRequestRD")
generate_documentation("InterpretationRequestCancer")
generate_documentation("InterpretedGenomesRD")
generate_documentation("InterpretedGenomesCancer")
generate_documentation("CancerParticipant")
generate_documentation("GelBamMetrics")
generate_documentation("AuditLog")
generate_documentation("RDParticipantChangeLog")
generate_documentation("MDTDeliveryProtocol")
generate_documentation("EvidenceSet")
generate_documentation("Comment")
generate_documentation("SequenceOntology")
generate_documentation("ReportEventContainer")
generate_documentation("ObservedVariant")
generate_documentation("ConfidenceInformationOntology")
generate_documentation("OntologyTerms")
generate_documentation("SupplementaryAnalysisResults")
generate_documentation("ExitQuestionnaire")
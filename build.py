import json
import os

import sys
import fnmatch

__author__ = 'antonior'

BASE_DIR = os.path.dirname(__file__)

if len(sys.argv) > 1:
    v = sys.argv[1]
else:
    v = 'latest'

module_version = v.replace('.', '_')

schemas = os.path.join(BASE_DIR, "schemas/IDLs", v, "org.gel.models.report.avro")
ga4gh_schemas = os.path.join(BASE_DIR, "schemas/IDLs", v, "org.ga4gh.models")
openCB_schemas = os.path.join(BASE_DIR, "schemas/IDLs", v, "org.opencb.biodata.models.sequence")
cva_schemas = os.path.join(BASE_DIR, "schemas/IDLs", v, "org.gel.models.cva.avro")
if v == 'latest':
    outfile = os.path.join(BASE_DIR, "protocols", "GelProtocols.py")
else:
    outfile = os.path.join(BASE_DIR, "protocols", "GelProtocols_{version}.py".format(version=module_version))


ga4gh_outfile = os.path.join(BASE_DIR, "protocols", "GA4GHProtocols.py")
openCB_outfile = os.path.join(BASE_DIR, "protocols", "openCBProtocols.py")
cva_outfile = os.path.join(BASE_DIR, "protocols", "CVAProtocols.py")
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

for idl in idls:
    print "transforming: " + idl
    base = os.path.basename(idl).replace(".avdl", "")
    os.system("java -jar " + avro_tools_jar + " idl2schemata " + idl + " " + os.path.join(json_folder, base))
    os.system("java -jar " + avro_tools_jar + " idl " + idl + " " + os.path.join(avrp_folder, base + ".avpr"))


VERSION = json.load(open(os.path.join(json_folder, "VersionControl", "VersionControl.avsc")))["fields"][0]["default"]

print ("version: " + VERSION)


os.system("python " + os.path.join(BASE_DIR, "resources", "CodeGenerationFromGA4GH", "process_schemas.py --outputFile "
                                   + outfile + " --avro-tools-jar " + avro_tools_jar + " --inputSchemasDirectory "
                                   + schemas + " " + VERSION))


os.system("python " + os.path.join(BASE_DIR, "resources", "CodeGenerationFromGA4GH", "process_schemas.py --outputFile "
                                   + ga4gh_outfile + " --avro-tools-jar " + avro_tools_jar + " --inputSchemasDirectory "
                                   + ga4gh_schemas + " " + VERSION))

os.system("python " + os.path.join(BASE_DIR, "resources", "CodeGenerationFromGA4GH", "process_schemas.py --outputFile "
                                   + openCB_outfile + " --avro-tools-jar " + avro_tools_jar + " --inputSchemasDirectory "
                                   + openCB_schemas + " " + VERSION))

os.system("python " + os.path.join(BASE_DIR, "resources", "CodeGenerationFromGA4GH", "process_schemas.py --outputFile "
                                   + cva_outfile + " --avro-tools-jar " + avro_tools_jar + " --inputSchemasDirectory "
                                   + cva_schemas + " " + VERSION))


os.system("avrodoc " + os.path.join(avrp_folder, "RDParticipant.avpr") + " > " + os.path.join(html_folder, "RDParticipant.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "ClinicalReportRD.avpr") + " > " + os.path.join(html_folder, "ClinicalReportRD.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "ClinicalReportCancer.avpr") + " > " + os.path.join(html_folder, "ClinicalReportCancer.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "InterpretationRequestRD.avpr") + " > " + os.path.join(html_folder, "RDInterpretationRequests.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "InterpretationRequestCancer.avpr") + " > " + os.path.join(html_folder, "CancerInterpretationRequests.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "InterpretedGenomesRD.avpr") + " > " + os.path.join(html_folder, "RDInterpretedGenomes.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "InterpretedGenomesCancer.avpr") + " > " + os.path.join(html_folder, "CancerInterpretedGenomes.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "CancerParticipant.avpr") + " > " + os.path.join(html_folder, "CancerParticipant.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "GelBamMetrics.avpr") + " > " + os.path.join(html_folder, "GelBamMetrics.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "AuditLog.avpr") + " > " + os.path.join(html_folder, "AuditLog.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "RDParticipantChangeLog.avpr") + " > " + os.path.join(html_folder, "RDParticipantChangeLog.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "MDTDeliveryProtocol.avpr") + " > " + os.path.join(html_folder, "MDTDeliveryProtocol.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "EvidenceSet.avpr") + " > " + os.path.join(html_folder, "EvidenceSet.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "Comment.avpr") + " > " + os.path.join(html_folder, "Comment.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "SequenceOntology.avpr") + " > " + os.path.join(html_folder, "SequenceOntology.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "ReportEventContainer.avpr") + " > " + os.path.join(html_folder, "ReportEventContainer.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "ObservedVariant.avpr") + " > " + os.path.join(html_folder, "ObservedVariant.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "ConfidenceInformationOntology.avpr") + " > " + os.path.join(html_folder, "ConfidenceInformationOntology.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "OntologyTerms.avpr") + " > " + os.path.join(html_folder, "OntologyTerms.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "SupplementaryAnalysisResults.avpr") + " > " + os.path.join(html_folder, "SupplementaryAnalysisResults.html"))
os.system("avrodoc " + os.path.join(avrp_folder, "ExitQuestionnaire.avpr") + " > " + os.path.join(html_folder, "ExitQuestionnaire.html"))

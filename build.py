import glob
import json
import os

__author__ = 'antonior'

BASE_DIR = os.path.dirname(__file__)

schemas = os.path.join(BASE_DIR, "schemas", "IDLs")
ga4gh_schemas = os.path.join(BASE_DIR, "ga4ghSchemas", "IDLs")
openCB_schema = os.path.join(BASE_DIR, "openCBschema", "IDLs")
outfile = os.path.join(BASE_DIR, "protocols", "GelProtocols.py")
ga4gh_outfile = os.path.join(BASE_DIR, "protocols", "GA4GHProtocols.py")
openCB_outfile = os.path.join(BASE_DIR, "protocols", "openCBProtocols.py")
avro_tools_jar = os.path.join(BASE_DIR, "resources", "bin", "avro-tools-1.7.7.jar")

for idl in glob.glob(os.path.join(BASE_DIR, "schemas", "IDLs", "*.avdl")):
    print "transforming: " + idl
    base = os.path.basename(idl).replace(".avdl", "")
    os.system("java -jar " + avro_tools_jar + " idl2schemata " + idl + " " +
              os.path.join(BASE_DIR, "schemas", "JSONs", base))

    os.system("java -jar " + avro_tools_jar + " idl " + idl + " " +
              os.path.join(BASE_DIR, "schemas", "AVPRs", base + ".avpr"))


VERSION = json.load(open(os.path.join(BASE_DIR, "schemas", "JSONs", "VersionControl", "VersionControl.avsc")))["fields"][0]["default"]

print ("version: " + VERSION)


os.system("python " + os.path.join(BASE_DIR, "resources", "CodeGenerationFromGA4GH", "process_schemas.py --outputFile "
                                   + outfile + " --avro-tools-jar " + avro_tools_jar + " --inputSchemasDirectory "
                                   + schemas + " " + VERSION))


os.system("python " + os.path.join(BASE_DIR, "resources", "CodeGenerationFromGA4GH", "process_schemas.py --outputFile "
                                   + ga4gh_outfile + " --avro-tools-jar " + avro_tools_jar + " --inputSchemasDirectory "
                                   + ga4gh_schemas + " " + VERSION))

os.system("python " + os.path.join(BASE_DIR, "resources", "CodeGenerationFromGA4GH", "process_schemas.py --outputFile "
                                   + openCB_outfile + " --avro-tools-jar " + avro_tools_jar + " --inputSchemasDirectory "
                                   + openCB_schema + " " + VERSION))




os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "RDParticipant.avpr") + " > " + os.path.join(BASE_DIR, "docs", "html_schemas", "RDParticipant.html"))
os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "ClinicalReportRD.avpr") + " > " + os.path.join(BASE_DIR, "docs", "html_schemas", "ClinicalReportRD.html"))
os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "ClinicalReportCancer.avpr") + " > " + os.path.join(BASE_DIR, "docs", "html_schemas", "ClinicalReportCancer.html"))
os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "InterpretationRequestRD.avpr") + " > " + os.path.join(BASE_DIR, "docs", "html_schemas", "RDInterpretationRequests.html"))
os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "InterpretationRequestCancer.avpr") + " > " + os.path.join(BASE_DIR, "docs", "html_schemas", "CancerInterpretationRequests.html"))
os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "InterpretedGenomesRD.avpr") + " > " + os.path.join(BASE_DIR, "docs", "html_schemas", "RDInterpretedGenomes.html"))
os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "InterpretedGenomesCancer.avpr") + " > " + os.path.join(BASE_DIR, "docs", "html_schemas", "CancerInterpretedGenomes.html"))
os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "CancerParticipant.avpr") + " > " + os.path.join(BASE_DIR, "docs", "html_schemas", "CancerParticipant.html"))
os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "GelBamMetrics.avpr") + " > " + os.path.join(BASE_DIR, "docs", "html_schemas", "GelBamMetrics.html"))
os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "AuditLog.avpr") + " > " + os.path.join(BASE_DIR, "docs", "html_schemas", "AuditLog.html"))
os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "RDParticipantChangeLog.avpr") + " > " + os.path.join(BASE_DIR, "docs", "html_schemas", "RDParticipantChangeLog.html"))
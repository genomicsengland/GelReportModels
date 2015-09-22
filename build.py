import glob
import os

__author__ = 'antonior'

BASE_DIR = os.path.dirname(__file__)
VERSION = "0.2.0"


schemas = os.path.join(BASE_DIR, "schemas", "IDLs")
ga4gh_schemas = os.path.join(BASE_DIR, "ga4ghSchemas", "IDLs")
outfile = os.path.join(BASE_DIR, "protocols", "GelProtocols.py")
ga4gh_outfile = os.path.join(BASE_DIR, "protocols", "GA4GHProtocols.py")
avro_tools_jar = os.path.join(BASE_DIR, "resources", "bin", "avro-tools-1.7.7.jar")

for idl in glob.glob(os.path.join(BASE_DIR, "schemas", "IDLs", "*.avdl")):
    print "transforming: " + idl
    base = os.path.basename(idl).replace(".avdl", "")
    os.system("java -jar " + avro_tools_jar + " idl2schemata " + idl + " " +
              os.path.join(BASE_DIR, "schemas", "JSONs", base))

    os.system("java -jar " + avro_tools_jar + " idl " + idl + " " +
              os.path.join(BASE_DIR, "schemas", "AVPRs", base + ".avpr"))


os.system("python " + os.path.join(BASE_DIR, "resources", "CodeGenerationFromGA4GH", "process_schemas.py --outputFile "
                                   + outfile + " --avro-tools-jar " + avro_tools_jar + " --inputSchemasDirectory "
                                   + schemas + " " + VERSION))


os.system("python " + os.path.join(BASE_DIR, "resources", "CodeGenerationFromGA4GH", "process_schemas.py --outputFile "
                                   + ga4gh_outfile + " --avro-tools-jar " + avro_tools_jar + " --inputSchemasDirectory "
                                   + ga4gh_schemas + " " + VERSION))

os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "RDParticipant.avpr") + " > " + os.path.join(BASE_DIR, "doc", "html_schemas", "RDParticipant.html"))
os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "InterpretationRequestRD.avpr") + " > " + os.path.join(BASE_DIR, "doc", "html_schemas", "InterpretationRequestRD.html"))
os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "InterpretedGenomesRD.avpr") + " > " + os.path.join(BASE_DIR, "doc", "html_schemas", "InterpretedGenomesRD.html"))
os.system("avrodoc " + os.path.join(BASE_DIR, "schemas", "AVPRs", "CancerParticipant.avpr") + " > " + os.path.join(BASE_DIR, "doc", "html_schemas", "CancerParticipant.html"))
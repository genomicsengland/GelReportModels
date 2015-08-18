import glob
import os

__author__ = 'antonior'

BASE_DIR = os.path.dirname(__file__)
VERSION = "0.2.0"


schemas = os.path.join(BASE_DIR, "schemas", "IDLs")
outfile = os.path.join(BASE_DIR, "protocols", "GelProtocols.py")
print outfile
avro_tools_jar = os.path.join(BASE_DIR, "resources", "bin", "avro-tools-1.7.7.jar")

for idl in glob.glob(os.path.join(BASE_DIR, "schemas", "IDLs", "*.avdl")):
    print "transforming: " + idl
    base = os.path.basename(idl).replace(".avdl", "")
    os.system("java -jar " + avro_tools_jar + " idl2schemata " + idl + " " +
              os.path.join(BASE_DIR, "schemas", "JSONs", base))


os.system("python " + os.path.join(BASE_DIR, "resources", "CodeGenerationFromGA4GH", "process_schemas.py --outputFile "
                                   + outfile + " --avro-tools-jar " + avro_tools_jar + " --inputSchemasDirectory "
                                   + schemas + " " + VERSION))
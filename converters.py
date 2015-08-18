import glob
import os

__author__ = 'antonior'

BASE_DIR = os.path.dirname(__file__)
print BASE_DIR
print glob.glob(os.path.join(BASE_DIR, "schemas", "IDLs", "*.avdl"))
for idl in glob.glob(os.path.join(BASE_DIR, "schemas", "IDLs", "*.avdl")):
    print "transforming: " + idl
    base = os.path.basename(idl).replace(".avdl", "")
    os.system("java -jar " + os.path.join(BASE_DIR, "resources", "bin", "avro-tools-1.7.7.jar") + " idl2schemata " +
              idl + " " + os.path.join(BASE_DIR, "schemas", "JSONs", base))


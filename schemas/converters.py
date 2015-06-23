import os

__author__ = 'antonior'

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

os.system("java -jar " + os.path.join(BASE_DIR, "resources", "avro-tools-1.7.7.jar") + " idl2schemata " +
                  os.path.join(BASE_DIR, "schemas", "IDLs", "CancerParticipant.avdl") + " "
                  + os.path.join(BASE_DIR, "schemas", "JSONs", "CancerParticipant"))
os.system("java -jar " + os.path.join(BASE_DIR, "resources", "avro-tools-1.7.7.jar") + " idl2schemata " +
                  os.path.join(BASE_DIR, "schemas", "IDLs", "InterpretationRequestRD.avdl") + " "
                  + os.path.join(BASE_DIR, "schemas", "JSONs", "ReportTriggeringRD"))
os.system("java -jar " + os.path.join(BASE_DIR, "resources", "avro-tools-1.7.7.jar") + " idl2schemata " +
                  os.path.join(BASE_DIR, "schemas", "IDLs", "InterpretedGenomesRD.avdl") + " "
                  + os.path.join(BASE_DIR, "schemas", "JSONs", "InterpretedGenomesRD"))
os.system("java -jar " + os.path.join(BASE_DIR, "resources", "avro-tools-1.7.7.jar") + " idl2schemata " +
                  os.path.join(BASE_DIR, "schemas", "IDLs", "RDParticipant.avdl") + " "
                  + os.path.join(BASE_DIR, "schemas", "JSONs", "RDParticipant"))
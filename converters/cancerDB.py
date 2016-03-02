import json
import os
import sys
import DataModels
from collections import defaultdict
import protocols.GelProtocols
from labkey.utils import create_server_context
from labkey.query import select_rows

__author__ = 'mparker,antonior'

labkey_server = 'gmc.genomicsengland.nhs.uk'
project_name = 'CRUK'  # Project folder name
contextPath = 'rdpilot-labkey'
schema = 'lists'
query = 'Patient'

server_context = create_server_context(labkey_server, project_name, contextPath, use_ssl=True)
result = select_rows(server_context, schema_name=schema, query_name=query)
labkey = defaultdict()
if result is not None:
    for record in result['rows']:
        labkey[record["local_patient_identifier"]]=record
else:
    print('select_rows: Failed to load results from ' + schema + '.' + table)

#print json.dumps(labkey,indent=True)


import MySQLdb
import xlrd
import xlwt
# passw = sys.argv[1]
passw = "pa55w0rd"
db = MySQLdb.connect("10.0.32.42","pipeline",passw,"gel_cancer_refactored")
cursor = db.cursor()
#cursor.execute("select samples.sample_id, sample_ids.participant_id, samples.lab_no, samples.well_id, samples.gel_id,samples.type, sample_types.type, modifier, center_patient_id, CENTER, pilot, TUMOR, gender from samples, sample_types, patients, sample_ids where samples.gel_id = patients.gel_id and samples.type = sample_types.id and sample_ids.gel_id = samples.gel_id ;")
#cursor.execute("select * from patients join sample_ids on patients.gel_id = sample_ids.gel_id where patients.tumor='CLL'")
cursor.execute("select * from patients, sample_ids where sample_ids.gel_id = patients.gel_id and pilot='CRUK'")
row = cursor.fetchone()
all_cancer_participant = {}
all_cancer_samples_tumor = {}
all_cancer_samples_normal = {}
well_ids = {}
while row is not None:
    sample = {}
    participant = {}

    num_fields = len(cursor.description)
    field_names = [i[0] for i in cursor.description]
    data = {key: value for key, value in zip(field_names, row)}

    sensitive=protocols.GelProtocols.SensitiveInformation()
    sensitive.originatingCenter=data["center"].lower()
    sensitive.centerPatientId=data["center_patient_id"]
    sensitive.gelID=data["participant_id"]

    cancer_participant=protocols.GelProtocols.CancerParticipant()
    cancer_participant.cancerSamples=list()
    cancer_participant.matchedSamples=list()

    cancer_demo=protocols.GelProtocols.CancerDemographics()

    if data["gender"] == "M":
        cancer_demo.sex = "male"
    if data["gender"] == "F":
        cancer_demo.sex = "female"

    #male is 1 female 2
    if data["center_patient_id"] in labkey:
        labkey_gender = str(labkey[data["center_patient_id"]]["sex"])

        labkey_gender = labkey_gender.replace("1","male")
        labkey_gender = labkey_gender.replace("2","female")

        if cancer_demo.sex != labkey_gender:
            print data["center_patient_id"] + " WRONG SEX (labkey "+ str(labkey_gender) +" manifest " + str(cancer_demo.sex) + " )"
    else:
        print data["center_patient_id"] + " NOT IN LABKEY"

    cancer_demo.gelId=data["participant_id"]

    cancer_participant.cancerDemographics=cancer_demo

    samples_cursor = db.cursor()
    query = "select * from samples join sample_types on samples.type=sample_types.id where gel_id='" + data["gel_id"] + "'"
    samples_cursor.execute(query)
    samples_row = samples_cursor.fetchone()
    all_cancer_samples_tumor = list()
    all_cancer_samples_normal = list()
    all_ids = list()
    while samples_row is not None:
        num_fields_sample = len(samples_cursor.description)
        field_names_samples = [i[0] for i in samples_cursor.description]
        sample_data = {key: value for key, value in zip(field_names_samples, samples_row)}
        cancer_sample=protocols.GelProtocols.CancerSample()
        cancer_sample.sampleId=sample_data["well_id"]
        all_ids.append(sample_data["well_id"])
        cancer_sample.labId=sample_data["lab_no"]
        if data["tumor"] != '':
            cancer_sample.sampleDiagnosis=data["tumor"].lower()
            cancer_demo.primaryDiagnosis=data["tumor"].lower()
        else:
            print data["center_patient_id"] + " NO TUMOR TYPE"
            cancer_sample.sampleDiagnosis="NA"
            cancer_demo.primaryDiagnosis="NA"
        cancer_sample.preservationMethod=sample_data["modifier"].lower()
        cancer_sample.gelPhase=data["pilot"].lower()
        if sample_data["type"] == "GL":
            cancer_sample.sampleType = "germline"
            #matched.germlineSampleId=sample_data["well_id"]
            all_cancer_samples_normal.append(sample_data["well_id"])
            if sample_data["id"] == 6:
                cancer_sample.source = "saliva"
            elif sample_data["id"] == 3:
                cancer_sample.source = "blood"
            else:
                cancer_sample.source = "tissue"

        else:
            cancer_sample.sampleType = "tumor"
            cancer_sample.sampleDiagnosis = data["tumor"].lower()

            if data["tumor"] == "CLL":
                cancer_sample.source = "blood"
                cancer_sample.method = "blood"
            else:
                cancer_sample.source = "tissue"
                type_cursor = db.cursor()
                query = "select value from sample_path_attributes where attribute = 'SAMPLE_TYPE' and sample_id=" + str(sample_data["sample_id"])
                type_cursor.execute(query)
                type_row = type_cursor.fetchall()
                for result in type_row:
                    for value in result:
                        cancer_sample.method=value.lower()

            #cancer_sample.source = data["tumor"].lower()
            #matched.tumorSampleId=sample_data["well_id"]
            all_cancer_samples_tumor.append(sample_data["well_id"])

        cancer_participant.cancerSamples.append(cancer_sample)

        samples_row = samples_cursor.fetchone()

    for tumor in all_cancer_samples_tumor:
        matched=protocols.GelProtocols.MatchedSamples()
        matched.tumorSampleId=tumor
        if len(all_cancer_samples_normal) > 0:
            matched.germlineSampleId=all_cancer_samples_normal[0]
            cancer_participant.matchedSamples.append(matched)
        else:
            print data["center_patient_id"] + " SOMETHING WRONG WITH MATCHED"


    cancer_demo.sampleId = all_ids

    row = cursor.fetchone()


    validate = cancer_participant.validate(cancer_participant.toJsonDict())
    if validate:
        print json.dumps(cancer_participant.toJsonDict(), indent=True)
    print json.dumps(cancer_participant.toJsonDict(), indent=True)




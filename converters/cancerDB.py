import json
import os
import sys

__author__ = 'antonior'

import MySQLdb
import xlrd
import xlwt
# passw = sys.argv[1]
passw = "pa55w0rd"
db = MySQLdb.connect("10.0.32.42","pipeline",passw,"gel_cancer")
cursor = db.cursor()
cursor.execute("select sample_ids.participant_id,  samples.well_id, samples.gel_id,samples.type, sample_types.type, modifier, center_patient_id, CENTER, pilot, TUMOR, gender from samples, sample_types, patients, sample_ids where samples.gel_id = patients.gel_id and samples.type = sample_types.id and sample_ids.gel_id = samples.gel_id ;")
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

    sample["centerSampleId"] = data["center_patient_id"]
    sample["id"] = data["well_id"]
    participant["id"] = data["participant_id"]
    participant["originatingCenter"] = data["CENTER"]
    participant["gelPhase"] = data["pilot"]
    participant["centerPatientId"] = data["center_patient_id"]
    participant["primaryDiagnosis"] = data["TUMOR"]
    participant["dataModelVersion"] = "0.0"
    if data["gender"] == "M":
        participant["sex"] = "male"
    if data["gender"] == "F":
        participant["sex"] = "female"

    participant["consentStatus"] = {"programmeConset": True, "primaryFindingConsent": False,
                                    "secondaryFindingConsent": False, "carrierStatusConsent": False}
    sample["source"] = data["modifier"]

    if data["type"] == "GL":
        sample["sampleType"]= "germline"
        all_cancer_samples_normal[data["center_patient_id"]] = sample
        all_cancer_participant[data["center_patient_id"]] = participant
    else:
        sample["sampleType"] = "tumor"
        all_cancer_samples_tumor[data["center_patient_id"]] = sample

    if participant["id"] in well_ids:
        well_ids[participant["id"]].append(data["well_id"])
    else:
        well_ids[participant["id"]] = [data["well_id"]]

    row = cursor.fetchone()


# tumor = sys.argv[2]
# normal = sys.argv[3]
# outdir = sys.argv[4]

# outdir = "/home/antonior/openclinica/cancer_annotation/"
# tumor = "/home/antonior/Downloads/gel_cruk_srf_patient_tumour_ffpe_1_1_0_2015-07-14_13-35.xlsx"
# tumor_xlsx = xlrd.open_workbook(tumor)
# tumor_sheet = tumor_xlsx.sheet_by_index(0)
#
# header = [str(cel.value) for cel in tumor_sheet.row(0)]
# for nrow in range(1, tumor_sheet.nrows):
#     values = [str(cel.value) for cel in tumor_sheet.row(nrow)]
#     data = {key: value for key, value in zip(header, values)}
#     id = data["Local Patient ID"]
#     if id in all_cancer_samples_tumor:
#         all_cancer_samples_tumor[id]["phase"] = data["Tumour Kind"].lower()
#         all_cancer_samples_normal[id]["phase"] = data["Tumour Kind"].lower()
#         all_cancer_samples_tumor[id]["method"] = data["Sample Type"].lower()
#         all_cancer_samples_normal[id]["method"] = data["Sample Type"].lower()
#         # all_cancer_samples_tumor[id]["cellularity"] = data[]
#         # all_cancer_samples_tumor[id]["phase"] = data[]
#         # if data["Tumour Type"].lower() != all_cancer_participant[id]["primaryDiagnosis"].lower():
#
#
#         fdw = file(os.path.join(outdir,  str(all_cancer_samples_tumor[id]["id"]) + "_" + "_sample.json"), "w")
#         json.dump(all_cancer_samples_tumor[id], fdw, indent=True)
#         fdw.close()
#
#         fdw = file(os.path.join(outdir,  str(all_cancer_samples_normal[id]["id"]) + "_" + "_sample.json"), "w")
#         json.dump(all_cancer_samples_normal[id], fdw, indent=True)
#         fdw.close()
#
#     else:
#         print id
#
#
# blood = "/home/antonior/Downloads/gel_cruk_srf_patient_tumour_ffpe_1_1_0_2015-07-14_13-35.xlsx"
# blood_xlsx = xlrd.open_workbook(tumor)
# blood_sheet = tumor_xlsx.sheet_by_index(0)
#
# header = [str(cel.value) for cel in blood_sheet.row(0)]
# for nrow in range(1, blood_sheet.nrows):
#     values = [str(cel.value) for cel in blood_sheet.row(nrow)]
#     data = {key: value for key, value in zip(header, values)}
#     id = data["Local Patient ID"]
#     if id in all_cancer_participant:
#         all_cancer_participant[id]["primaryDiagnosis"] = data["Tumour Type"]
#         if data["Patient Gender"] == "1":
#             all_cancer_participant[id]["sex"] = "male"
#         else:
#             all_cancer_participant[id]["sex"] = "female"
#
#
#         for well_id in well_ids[all_cancer_participant[id]["id"]]:
#             fdw = file(os.path.join(outdir,  well_id + "_" + "participant.json"), "w")
#             json.dump(all_cancer_participant[id], fdw, indent=True)
#             fdw.close()
#
#     else:
#         print id
#
#
#
#
#
#






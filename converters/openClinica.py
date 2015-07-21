import json
import os

__author__ = 'antonior'
from GelReportModels.protocols.GelProtcols import RDParticipant, Disorder, HpoTerm, ConsentStatus


terms ={
    "Study Subject ID": "id",
    "gel_rd_registrationandconsent_R_2_family_id": "FamilyId",
    "Secondary ID": "externalIds",
    "Sex": "sex",
    "gel_rd_phenotyping_DiseaseGroup_disease_group": "diseaseGroup",
    "gel_rd_phenotyping_DiseaseSubgroup_disease_subgroup": "diseaseSubGroup",
    "gel_rd_phenotyping_SpecificDisease_specific_disease": "specificDisease",
    "gel_rd_phenotyping_PT_3_phenotype_identifier": "term",
    "gel_rd_registrationandconsent_REL_3_disease_status": "carrierStatuscarrierStatus",
    "gel_rd_registrationandconsent_Cons_2_consent_given": "carrierStatusConsent",
    "gel_rd_registrationandconsent_ConsentStratificationText_consent_question": "secondaryFindingConsent"
}






def get_term(openc_term, terms):
    for key, value in terms.iteritems():
        if key in openc_term:
            return value
    return False


def open_clinicatab2GELmodel(tabfile, pedigree, folder):
    fd = file(tabfile)
    ped = file(pedigree)

    record_on = False
    header =[]
    samples = {}

    pedigree_data = json.load(ped)

    for record in pedigree_data:
        participant = RDParticipant()

        if "sex" in record:
            participant.sex = record["sex"]
        else:
            participant.sex = "UNKNOWN"
        if "father" in record:
            participant.father = record["father"]
        if "mother" in record:
            participant.mother = record["mother"]
        if "id" in record:
            participant.id = record["id"]

        else:
            raise StandardError("Not id field found!!")
        samples[participant.id] = participant

    for line in fd:
        if record_on:

            openclinica_data = {}
            openclinica_data["hpo_terms"] = []
            openclinica_data["carrierStatuscarrierStatus"] = []
            openclinica_data["diseaseGroup"] = []
            openclinica_data["diseaseSubGroup"] = []
            openclinica_data["specificDisease"] = []
            aline = line.rstrip("\n").split("\t")
            data = {key: value for key,value in zip(header, aline)}

            for key, value in data.iteritems():
                term = get_term(key.lstrip("\n").rstrip("\n"), terms)
                try:
                    value = int(value)
                except:
                    value = value
                if term:
                    if term == "term" and value != '':
                        openclinica_data["hpo_terms"].append(value)
                    elif term == "carrierStatuscarrierStatus" and value != '':
                        openclinica_data["carrierStatuscarrierStatus"].append(value)
                    elif term == "diseaseGroup" and value != '':
                        openclinica_data["diseaseGroup"].append(value)
                    elif term == "diseaseSubGroup" and value != '':
                        openclinica_data["diseaseSubGroup"].append(value)
                    elif term == "specificDisease" and value != '':
                        openclinica_data["specificDisease"].append(value)
                    else:
                        openclinica_data[term] = value

            if openclinica_data["id"] in samples:
                id = openclinica_data["id"]
                if openclinica_data["FamilyId"] != "":
                    samples[id].FamilyId = openclinica_data["FamilyId"]
                else:
                    raise StandardError("Sample " + id + " don't have familyID information")

                diseases = zip(openclinica_data["diseaseGroup"], openclinica_data["diseaseSubGroup"], openclinica_data["specificDisease"])
                samples[id].disorderList = []
                for disease in diseases:
                    disorder = Disorder()
                    disorder.diseaseGroup = disease[0]
                    disorder.diseaseSubGroup = disease[1]
                    disorder.specificDisease = disease[2]
                    disorder.ageOfOnset = None
                    samples[id].disorderList.append(disorder)
                if samples[id].disorderList == []:
                    samples[id].disorderList = None

                samples[id].hpoTermList = []
                for hpo in openclinica_data["hpo_terms"]:
                    hpo_term = HpoTerm()
                    hpo_term.term = hpo
                    samples[id].hpoTermList.append(hpo_term)
                if samples[id].hpoTermList == []:
                    samples[id].hpoTermList = None

                consent = ConsentStatus()
                consent.programmeConset = True
                if openclinica_data["carrierStatusConsent"] == "Yes":
                    consent.carrierStatusConsent = True
                else:
                    consent.carrierStatusConsent = False

                if openclinica_data["secondaryFindingConsent"] == "Yes":
                    consent.carrierStatusConsent = True
                else:
                    consent.carrierStatusConsent = False

                samples[id].consentStatus = consent

                samples[id].dataModelCatalogueVersion = "0.0"

        if line.startswith("Study Subject ID"):
            record_on = True
            header = line.split("\t")

    for sample in samples:
        fdw = file(os.path.join(folder, str(sample) + "_rd_model.json"), "w")
        json.dump(samples[sample].toJsonDict(), fdw, indent=True)



open_clinicatab2GELmodel("/home/antonior/openclinica/expample.tab.csv", "/home/antonior/openclinica/P3_2.json", "/home/antonior/openclinica")
import json
import os
import sys
from GelReportModels.conectors import MySql

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
    "gel_rd_registrationandconsent_DiseaseGroup_disease_group_E1_C1": "diseaseGroup",
    "gel_rd_registrationandconsent_DiseaseSubgroup_disease_subgroup_E1_C1": "diseaseSubGroup",
    "gel_rd_registrationandconsent_SpecificDisease_specific_disease_E1_C1": "specificDisease",
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

def map_identifiers(tabfiles):

    maps = file("/home/antonior/PycharmProjects/SchemaAvro/tomap")
    fdw = file("/home/antonior/PycharmProjects/SchemaAvro/maped", "w")

    individuals = []

    ids = file("/home/antonior/PycharmProjects/SchemaAvro/ids_mapping.txt")
    mapping_ids = {}
    for line in ids:
        aline = line.rstrip("\n").split("\t")
        mapping_ids[aline[0]] = int(aline[1])


    for tabfile in tabfiles:
        header = []
        record_on = False
        fd = file(tabfile)
        for line in fd:
            if record_on:
                aline = line.rstrip("\n").split("\t")
                data = {key: value for key,value in zip(header, aline)}
                record = {}
                record["id"] =mapping_ids[str(data["Study Subject ID"]) + "_" + str(data[" gel_rd_registrationandconsent_R_2_family_id_E1_C1 "])]
                record["name"] = data[" gel_rd_registrationandconsent_R_10_forenames_E1_C1 "]
                record["surname"] = data[" gel_rd_registrationandconsent_R_8_surname_E1_C1 "]
                record["dob"] = data[" gel_rd_registrationandconsent_R_3_date_of_birth_E1_C1 "]
                individuals.append(record)

            if line.startswith("Study Subject ID"):
                record_on = True
                header = line.split("\t")

    names = [(r["surname"], r["name"]) for r in individuals]

    mappings = {}
    for line in maps:
        aline = line.rstrip("\n").split("\t")
        mappings[(aline[2], aline[3])] = aline[0]
        mappings[aline[4]] = aline[0]

    for r in individuals:
        if (r["surname"], r["name"]) in mappings:
            fdw.write(mappings[(r["surname"], r["name"])] + "\t" + str(r["id"]) +"\n")
        elif r["dob"] in mappings:
            fdw.write(mappings[r["dob"]] + "\t" + str(r["id"]) +"\n")
        else:
            pass







def create_ped(tabfile, out_dir):
    fd = file(tabfile)
    record_on = False

    pedigrees = {}
    header = []
    for line in fd:
        if record_on:
            aline = line.rstrip("\n").split("\t")
            data = {key: value for key,value in zip(header, aline)}

            record = {}
            record["id"] = data["Study Subject ID"]
            record["relation"] = data[" gel_rd_registrationandconsent_REL_1_biological_relationship_to_proband_E1_C1 "]
            record["type"] = data[" gel_rd_registrationandconsent_ParticipantType_what_type_of_participant_are_you_registering_E1_C1 "]
            record["sex"] = data[" gel_rd_registrationandconsent_R_11_gender_E1_C1 "]

            if data[" gel_rd_registrationandconsent_R_2_family_id_E1_C1 "] in pedigrees:
                pedigrees[data[" gel_rd_registrationandconsent_R_2_family_id_E1_C1 "] ].append(record)
            else:
                pedigrees[data[" gel_rd_registrationandconsent_R_2_family_id_E1_C1 "] ] =[record]

        if line.startswith("Study Subject ID"):
            record_on = True
            header = line.split("\t")

    for ped in pedigrees:
        family = pedigrees[ped]
        new_family = []
        for ind in family:
            member = {}
            member["id"] = ind["id"]

            if ind["sex"] == "1":
                member["sex"] = "male"
            else:
                member["sex"] = "female"

            if ind["type"] == "Proband":
                try:
                    mother = [participant["id"] for participant in family if participant["relation"] == "Mother"][0]
                    member["mother"] = mother
                except:
                    pass
                try:
                    father = [participant["id"] for participant in family if participant["relation"] == "Father"][0]
                    member["father"] = father
                except:
                    pass

            elif ind["relation"] == "FullSibling":

                try:
                    mother = [participant["id"] for participant in family if participant["relation"] == "Mother"][0]

                    member["mother"] = mother
                except:
                    pass
                try:
                    father = [participant["id"] for participant in family if participant["relation"] == "Father"][0]
                    member["father"] = father
                except:
                    pass

            elif ind["relation"] == "Mother":
                try:
                    mother = [participant["id"] for participant in family if participant["relation"] == "MaternalGrandmother"][0]
                    member["mother"] = mother
                except:
                    pass
                try:
                    father = [participant["id"] for participant in family if participant["relation"] == "MaternalGrandfather"][0]
                    member["father"] = father
                except:
                    pass

            elif ind["relation"] == "MaternalAunt":
                try:
                    mother = [participant["id"] for participant in family if participant["relation"] == "MaternalGrandmother"][0]
                    member["mother"] = mother
                except:
                    pass
                try:
                    father = [participant["id"] for participant in family if participant["relation"] == "MaternalGrandfather"][0]
                    member["father"] = father
                except:
                    pass

            elif ind["relation"] == "MaternalCousinSister":
                try:
                    mother = [participant["id"] for participant in family if participant["relation"] == "MaternalAunt"][0]
                    member["mother"] = mother
                except:
                    pass

            elif ind["relation"] == "Father":
                try:
                    mother = [participant["id"] for participant in family if participant["relation"] == "PaternalGrandmother"][0]
                    member["mother"] = mother
                except:
                    pass
                try:
                    father = [participant["id"] for participant in family if participant["relation"] == "PaternalGrandfather"][0]
                    member["father"] = father
                except:
                    pass
            new_family.append(member)
        fdw = file(out_dir + "/" + ped + ".json", "w")
        json.dump(new_family, fdw)



def open_clinicatab2GELmodel(tabfile, pedigree, folder):
    fd = file(tabfile)
    ped = file(pedigree)
    ids = file("/home/antonior/PycharmProjects/SchemaAvro/ids_mapping.txt")
    mapping_ids = {}
    for line in ids:
        aline = line.rstrip("\n").split("\t")
        mapping_ids[aline[0]] = int(aline[1])

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
        samples[str(participant.id)] = participant
    print samples
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
                    if term == "term":
                        if value != "":
                            openclinica_data["hpo_terms"].append(value)
                    elif term == "carrierStatuscarrierStatus":
                        if value != "":
                            openclinica_data["carrierStatuscarrierStatus"].append(value)
                    elif term == "diseaseGroup":
                        if value != "":
                            openclinica_data["diseaseGroup"].append(value)
                    elif term == "diseaseSubGroup":
                        if value != "":
                            openclinica_data["diseaseSubGroup"].append(value)
                    elif term == "specificDisease":
                        if value != "":
                            openclinica_data["specificDisease"].append(value)
                    else:
                        openclinica_data[term] = value

            openclinica_data["id"] = str(openclinica_data["id"])

            if openclinica_data["id"] in samples:
                id = openclinica_data["id"]
                samples[id].id = mapping_ids[str(openclinica_data["id"]) + "_" + str(openclinica_data["FamilyId"])]
                try:
                    samples[id].mother = mapping_ids[str(samples[id].mother) + "_" + str(openclinica_data["FamilyId"])]
                except:
                    pass
                try:
                    samples[id].father = mapping_ids[str(samples[id].father) + "_" + str(openclinica_data["FamilyId"])]
                except:
                    pass
                if openclinica_data["FamilyId"] != "":
                    samples[id].FamilyId = openclinica_data["FamilyId"]
                else:
                    raise StandardError("Sample " + id + " don't have familyID information")

                diseases = zip(set(openclinica_data["diseaseGroup"]), set(openclinica_data["diseaseSubGroup"]), set(openclinica_data["specificDisease"]))
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
                    samples[id].carrierStatus = "unaffected"
                else:
                    samples[id].carrierStatus = "affected"

                samples[id].hpoTermList = []
                for hpo in openclinica_data["hpo_terms"]:
                    hpo_term = HpoTerm()
                    hpo_term.term = hpo
                    samples[id].hpoTermList.append(hpo_term)
                if samples[id].hpoTermList == []:
                    samples[id].hpoTermList = None

                consent = ConsentStatus()
                consent.programmeConset = True
                consent.carrierStatusConsent = False
                consent.secondaryFindingConsent = False
                consent.primaryFindingConsent = False

                samples[id].consentStatus = consent

                samples[id].dataModelCatalogueVersion = "0.0"

        if line.startswith("Study Subject ID"):
            record_on = True
            header = line.split("\t")


    con = MySql.GelMySql("gel_RD")
    for sample in samples:
        try:
            lp = con.get_LP(str(samples[sample].id))
            fdw = file(os.path.join(folder, lp + "_rd_model.json"), "w")
            json.dump(samples[sample].toJsonDict(), fdw, indent=True)
            fdw.close()
        except:
            print  str(samples[sample].id)



    # fdw_family = file(os.path.join(folder, str(samples[sample_mock].FamilyId) + "_ped.json"), "w")
    # family = {"familyId": str(samples[sample].FamilyId), "participants": [samples[sample].toJsonDict() for sample in samples]}
    # json.dump(family, fdw_family, indent=True)
    # fdw_family.close()



# open_clinicatab2GELmodel("/home/antonior/openclinica/expample.tab.csv", "/home/antonior/openclinica/P3_2.json", "/home/antonior/openclinica")
# create_ped("/home/antonior/Desktop/openclinica/pilot3/TAB_data_out_2015-07-20-145855335.tsv", "/home/antonior/openclinica/p3/")

tab = sys.argv[2]
ped = sys.argv[1]
outdir = sys.argv[3]
#
open_clinicatab2GELmodel(tab, ped, outdir)


# map_identifiers(["/home/antonior/Desktop/openclinica/pilot3/TAB_data_out_2015-07-20-145855335.tsv", "/home/antonior/Desktop/openclinica/pilot2/TAB_all_data_2015-07-20-160641795.tsv"])

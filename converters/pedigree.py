__author__ = 'antonior'
import json
import os
import sys

from GelReportModels.protocols.GelProtcols import RDParticipant, Disorder, HpoTerm, ConsentStatus

# ped = sys.argv[1]
# outdir = sys.argv[2]

ped = "/home/antonior/Downloads/pedigree/pedigrees_using_participant_ids.fam"
links = "/home/antonior/Downloads/pedigree/links.txt"

pedigree_file = file(ped)
link = file(links)

links_ids ={}
for l in link:
    aline = l.rstrip("\n").replace("\r", "").split("\t")
    links_ids[int(aline[1])] = aline[0]



for line in pedigree_file:
    participant = RDParticipant()
    aline = line.rstrip("\n").replace("\r", "").split("\t")[0:7]
    record = {key: value for key, value in zip(["familyID", "id", "father", "mother", "sex", "status", "type"], aline)}

    if record["type"] != "withdrawn" and "NA" not in record.values():

        if record["sex"] == "1":
            participant.sex = "male"
        elif record["sex"] == "2":
            participant.sex = "female"
        else:
            participant.sex = "unknown"

        if record["status"] == "1":
            participant.carrierStatus = "unaffected"
        elif record["status"] == "2":
            participant.carrierStatus = "affected"
        else:
            participant.carrierStatus = "uncertain"

        participant.id = int(record["id"])
        participant.FamilyId = int(record["familyID"])
        participant.dataModelCatalogueVersion = "0.0"
        try:
            if int(record["father"]) != 0:
                participant.father = int(record["father"])
        except:
            pass

        try:
            if int(record["mother"]) != 0:
                 participant.mother = int(record["mother"])
        except:
            pass

        consensus = ConsentStatus()
        consensus.carrierStatusConsent = "False"
        consensus.programmeConset = "True"
        consensus.secondaryFindingConsent = "False"
        consensus.primaryFindingConsent = "False"

        participant.consentStatus = consensus
        fdw = file("/home/antonior/openclinica/pedigrees/"+links_ids[participant.id]+"_sample.json", "w")
        json.dump(participant.toJsonDict(), fdw)
        fdw.close()







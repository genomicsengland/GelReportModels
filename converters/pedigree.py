__author__ = 'antonior'
import json
import os
import sys

from GelReportModels.protocols.GelProtcols import RDParticipant, Disorder, HpoTerm, ConsentStatus

# ped = sys.argv[1]
# outdir = sys.argv[2]

ped = "/home/antonior/openclinica/pedigrees_using_participant_ids.fam"

pedigree_file = file(ped)

for line in pedigree_file:
    participant = RDParticipant()
    aline = line.rstrip("\n").split("\t")
    record = {key: value for key, value in zip(["familyID", "id", "father", "mother", "sex", "status", "type"], aline)}
    if record["type"] != "withdrawn":
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

        participant.id = record["id"]
        participant.father = record["father"]
        participant.mother = record["mother"]

        consensus = ConsentStatus()
        consensus.carrierStatusConsent = "False"
        consensus.programmeConset = "True"
        consensus.secondaryFindingConsent = "False"
        consensus.primaryFindingConsent = "False"

        participant.consentStatus = consensus

        print participant.toJsonDict()







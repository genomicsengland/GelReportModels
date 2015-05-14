import os
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter

from GelReportModels.protocols.protocolElement import ProtocolElement
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
__author__ = 'antonior'


class ConsentStatus(ProtocolElement):

    schema = avro.schema.parse(open("/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/ConsentStatus.avsc").read())

    _schemaSource = "/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/ConsentStatus.avsc"


    requiredFields = ({})

    @classmethod
    def isEmbeddedType(cls, fieldName):
        embeddedTypes = {}
        return fieldName in embeddedTypes

    @classmethod
    def getEmbeddedType(cls, fieldName):
        embeddedTypes = {}
        return embeddedTypes[fieldName]

    __slots__ = ["carrierStatusConsent",
                 "secondaryFindingConsent",
                 ]

    def __init__(self):
        self.secondaryFindingConsent = None
        self.carrierStatusConsent = None


class Disorder(ProtocolElement):

    schema = avro.schema.parse(open("/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/Disorder.avsc").read())

    _schemaSource = "/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/Disorder.avsc"


    requiredFields = ({"OMIMid", "DisorderName"})

    @classmethod
    def isEmbeddedType(cls, fieldName):
        embeddedTypes = {}
        return fieldName in embeddedTypes

    @classmethod
    def getEmbeddedType(cls, fieldName):
        embeddedTypes = {}
        return embeddedTypes[fieldName]

    __slots__ = ["OMIMid",
                 "DisorderName",
                 "ageOfOnset",
                 ]

    def __init__(self):
        self.OMIMid = None
        self.DisorderName = None
        self.ageOfOnset = None

class HpoTerm(ProtocolElement):

    schema = avro.schema.parse(open("/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/HpoTerm.avsc").read())

    _schemaSource = "/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/HpoTerm.avsc"


    requiredFields = ({"term"})

    @classmethod
    def isEmbeddedType(cls, fieldName):
        embeddedTypes = {}
        return fieldName in embeddedTypes

    @classmethod
    def getEmbeddedType(cls, fieldName):
        embeddedTypes = {}
        return embeddedTypes[fieldName]

    __slots__ = ["term",
                 "modifier",
                 "ageOfOnset",
                 ]

    def __init__(self):
        self.term = None
        self.modifier = None
        self.ageOfOnset = None

class File(ProtocolElement):

    schema = avro.schema.parse(open("/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/File.avsc").read())

    _schemaSource = "/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/File.avsc"


    requiredFields = ({"URIFile"})

    @classmethod
    def isEmbeddedType(cls, fieldName):
        embeddedTypes = {}
        return fieldName in embeddedTypes

    @classmethod
    def getEmbeddedType(cls, fieldName):
        embeddedTypes = {}
        return embeddedTypes[fieldName]

    __slots__ = ["URIFile",
                 "SampleId",
                 ]

    def __init__(self):
        self.URIFile = None
        self.SampleId = None


class VirtualPanel(ProtocolElement):

    schema = avro.schema.parse(open("/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/VirtualPanel.avsc").read())

    _schemaSource = "/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/VirtualPanel.avsc"


    requiredFields = ({"level4Title"})

    @classmethod
    def isEmbeddedType(cls, fieldName):
        embeddedTypes = {
            "RelevantRegions": File,
            "clinicalRelevantVariants": File,
        }
        return fieldName in embeddedTypes

    @classmethod
    def getEmbeddedType(cls, fieldName):
        embeddedTypes = {
            "RelevantRegions": File,
            "clinicalRelevantVariants": File,
        }
        return embeddedTypes[fieldName]

    __slots__ = ["level4Title",
                 "geneIds",
                 "clinicalRelevantTranscripts",
                 "RelevantRegions",
                 "clinicalRelevantVariants",
                 ]

    def __init__(self):
        self.level4Title = None
        self.geneIds = None
        self.clinicalRelevantTranscripts = None
        self.RelevantRegions = None
        self.clinicalRelevantVariants = None




class RDParticipant(ProtocolElement):

    schema = avro.schema.parse(open("/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/RDParticipant.avsc").read())

    _schemaSource = "/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/RDParticipant.avsc"


    requiredFields = ({"id", "dataModelVersion", "sex", "consentStatus"})

    @classmethod
    def isEmbeddedType(cls, fieldName):
        embeddedTypes = {
            "consentStatus": ConsentStatus,
            "HpoTerm": HpoTerm,
            "Disorder": ConsentStatus,

        }
        return fieldName in embeddedTypes

    @classmethod
    def getEmbeddedType(cls, fieldName):
        embeddedTypes = {
            "consentStatus": ConsentStatus,
            "HpoTerm": HpoTerm,
            "Disorder": ConsentStatus,
        }
        return embeddedTypes[fieldName]

    __slots__ = ["id",
                 "dataModelVersion",
                 "sex",
                 "consentStatus",
                 "externalIds",
                 "father",
                 "mother",
                 "disorders",
                 "hpoTerms",
                 "carrierStatus",
                 "twinGroup",
                 "monozygotic",
                 "adoptedStatus",
                 "consanguinityRelationship",
                 "additionalInformation",
                 ]

    def __init__(self):
        self.id = None
        self.dataModelVersion = None
        self.sex = None
        self.consentStatus = None
        self.externalIds = None
        self.father = None
        self.mother = None
        self.disorders = None
        self.hpoTerms = None
        self.carrierStatus = None
        self.lifeStatus = None
        self.twinGroup = None
        self.monozygotic = None
        self.adoptedStatus = None
        self.consanguinityRelationship = None
        self.additionalInformation = None

class Pedigree(ProtocolElement):

    schema = avro.schema.parse(open("/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/Pedigree.avsc").read())

    _schemaSource = "/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/Pedigree.avsc"


    requiredFields = ({"FamilyId", "participants"})

    @classmethod
    def isEmbeddedType(cls, fieldName):
        embeddedTypes = {
            "participants": RDParticipant,
        }
        return fieldName in embeddedTypes

    @classmethod
    def getEmbeddedType(cls, fieldName):
        embeddedTypes = {
            "participants": RDParticipant,
        }
        return embeddedTypes[fieldName]

    __slots__ = ["familyId",
                 "participants",
                 ]

    def __init__(self):
        self.familyId = None
        self.participants = None


class RareDisease(ProtocolElement):

    schema = avro.schema.parse(open("/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/RareDisease.avsc").read())

    _schemaSource = "/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/RareDisease.avsc"


    requiredFields = ({"level4Title", "pedigree", "modeOfInheritanceDescription"})

    @classmethod
    def isEmbeddedType(cls, fieldName):
        embeddedTypes = {
            "pedigree": Pedigree,
            "virtualPanel": VirtualPanel,
        }
        return fieldName in embeddedTypes

    @classmethod
    def getEmbeddedType(cls, fieldName):
        embeddedTypes = {
            "pedigree": Pedigree,
            "virtualPanel": VirtualPanel,
        }
        return embeddedTypes[fieldName]

    __slots__ = ["level4Title",
                 "pedigree",
                 "inbreedingCoefficientEstimates",
                 "complexGeneticPhenomenaDescription",
                 "modeOfInheritanceDescription",
                 "virtualPanel",
                 ]

    def __init__(self):
        self.level4Title = None
        self.pedigree = None
        self.inbreedingCoefficientEstimates = None
        self.complexGeneticPhenomenaDescription = None
        self.modeOfInheritanceDescription = None
        self.virtualPanel = None



class Report(ProtocolElement):

    schema = avro.schema.parse(open("/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/Report.avsc").read())

    _schemaSource = "/home/antonior/PycharmProjects/SchemaAvro/GelReportModels/schemas/JSONs/ReportTriggeringRD/Report.avsc"


    requiredFields = ({"id", "reportVersion", "BAMs", "gVCFs", "VCFs", "BigWigs", "annotationFile",
                       "rareDisease", "backReportURI", "backReportVersion"})

    @classmethod
    def isEmbeddedType(cls, fieldName):
        embeddedTypes = {
            "BAMs": File,
            "gVCFs": File,
            "VCFs": File,
            "BigWigs": File,
            "annotationFile": File,
        }
        return fieldName in embeddedTypes

    @classmethod
    def getEmbeddedType(cls, fieldName):
        embeddedTypes = {
            "BAMs": File,
            "gVCFs": File,
            "VCFs": File,
            "BigWigs": File,
            "annotationFile": File,
        }
        return embeddedTypes[fieldName]

    __slots__ = ["id",
                 "reportVersion",
                 "BAMs",
                 "gVCFs",
                 "VCFs",
                 "BigWigs",
                 "annotationFile",
                 "rareDisease",
                 "familyHistory",
                 "backReportURI",
                 "backReportVersion",
                 "additionalInfo",
                 ]

    def __init__(self):
        self.id = None
        self.reportVersion = None
        self.BAMs = None
        self.gVCFs = None
        self.VCFs = None
        self.BigWigs = None
        self.annotationFile = None
        self.rareDisease = None
        self.familyHistory = None
        self.backReportURI = None
        self.backReportVersion = None
        self.additionalInfo = None
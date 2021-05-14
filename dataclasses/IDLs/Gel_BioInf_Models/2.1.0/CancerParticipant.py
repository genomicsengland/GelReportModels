import dataclasses
from dataclasses import field
import random
from marshmallow import validate, ValidationError
from marshmallow_dataclass import dataclass, Optional
from .VersionControl import VersionControl
from .CommonParticipant import *

SampleType = {"germline", "tumor"}

PreservationMethod = {"FFPE", "FF", "UNKNOWN", "BLOOD", "GL", "SALIVA", "LEUK"}

Phase = {"PRIMARY", "METASTATIC", "RECURRENCE"}

GelPhase = {"CRUK", "OXFORD", "CLL", "IIP", "MAIN", "EXPT"}

Method = {"RESECTION", "BIOPSY", "BLOOD"}

Sex = {"M", "F"}


@dataclass
class CancerSample:
    sampleId: str
    labId: Optional[str]
    gelPhase: Optional[str] = field(default=None, metadata={"validate": validate.OneOf(GelPhase)})
    sampleType: Optional[str] = field(default=None, metadata={"validate": validate.OneOf(SampleType)})
    sampleDiagnosis: Optional[str]
    tumorType: Optional[str]
    tumorSubType: Optional[str]
    preservationMethod: Optional[str] = field(default=None,
                                               metadata={"validate": validate.OneOf(PreservationMethod)})

    phase: Optional[str] = field(default=None,
                                  metadata={"validate": validate.OneOf(Phase)})
    method: Optional[str] = field(default=None,
                                   metadata={"validate": validate.OneOf(Method)})
    cellularity: Optional[str] = field(default=None)
    tumorContent: Optional[str] = field(default=None)
    grade: Optional[str] = field(default=None)
    tmn_stage_version: Optional[str] = field(default=None)
    tmn_stage_grouping: Optional[str] = field(default=None)


@dataclass
class CancerDemographics:
    # TODO probably the IDs could be *integers* instead?
    gelId: str = field(metadata={"metadata": {
        "description": "Individual Id (this is the individual id (gel ID))"}})
    center: str
    centerPatientId: str
    labkeyParticipantId: Optional[str]
    primaryDiagnosis: Optional[str] = field(default=None, metadata={
        "metadata": {"description": "Source of the primary diagnosis site."},
        "validate": validate.OneOf(["blood", "breast", "prostate",
                                    "colorectal", "cll", "aml", "renal",
                                    "ovarian", "skin", "lymphNode", "bone", "saliva"])}
                                            )
    dataModelVersion: str = field(default="v2.4")
    sex: Optional[str] = field(default=None, metadata={"validate": validate.OneOf(Sex)})
    consentStatus: ConsentStatus
    additionalInformation: Optional[List[str]] = field(default=None,
                                                       metadata={
                                                           "description": "map here to store additional information"
                                                                          " for example URIs to images, ECGs, etc"
                                                       })
    sampleId: Optional[List[str]]
    assignedICD10: Optional[str]

@dataclass
class MatchedSamples:
    """This defines a pair of germline and tumor, this pair should/must be analyzed together"""
    germlineSampleId: Optional[str]
    tumorSampleId: Optional[str]


@dataclass
class CancerParticipant:

    versionControl: VersionControl
    cancerDemographics: CancerDemographics
    cancerSamples: List[CancerSample]
    matchedSamples: List[MatchedSamples]

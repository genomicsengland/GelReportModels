import dataclasses
from dataclasses import field
from marshmallow import validate
from marshmallow.fields import List, ValidationError
from marshmallow_dataclass import dataclass, Optional
from enum import Enum


Sex = {"male", "female", "unknown", "undetermined"}

PersonKaryotipicSex = {"unknown",
                       "XX",
                       "XY",
                       "XO",
                       "XXY",
                       "XXX",
                       "XXYY",
                       "XXXY",
                       "XXXX",
                       "XYY",
                       "other"}

TernaryOption = {"yes", "no", "unknown"}


class EthnicCategory(Enum):
    D = "Mixed: White and Black Caribbean"
    E = "Mixed: White and Black African"
    F = "Mixed: White and Asian"
    G = "Mixed: Any other mixed background"
    A = "White: British"
    B = "White: Irish"
    C = "White: Any other White background"
    L = "Asian or Asian British: Any other Asian background"
    M = "Black or Black British: Caribbean"
    N = "Black or Black British: African"
    H = "Asian or Asian British: Indian"
    J = "Asian or Asian British: Pakistani"
    K = "Asian or Asian British: Bangladeshi"
    P = "Black or Black British: Any other Black background"
    S = "Other Ethnic Groups: Any other ethnic group"
    R = "Other Ethnic Groups: Chinese"
    Z = "Not stated"


class KGPopCategory(Enum):
    ACB = "ACB"
    ASW = "ASW"
    BEB = "BEB"
    CDX = "CDX"
    CEU = "CEU"
    CHB = "CHB"
    CHS = "CHS"
    CLM = "CLM"
    ESN = "ESN"
    FIN = "FIN"
    GBR = "GBR"
    GIH = "GIH"
    GWD = "GWD"
    IBS = "IBS"
    ITU = "ITU"
    JPT = "JPT"
    KHV = "KHV"
    LWK = "LWK"
    MSL = "MSL"
    MXL = "MXL"
    PEL = "PEL"
    PJL = "PJL"
    PUR = "PUR"
    STU = "STU"
    TSI = "TSI"
    YRI = "YRI"


class kGSuperPopCategory(Enum):
    AFR = "AFR"
    AMR = "AMR"
    EAS = "EAS"
    EUR = "EUR"
    SAS = "SAS"


@dataclass
class chiSquare1KGenomesPhase3Pop:
    """Chi-square test for goodness of fit of this sample to 1000 Genomes Phase 3 populations"""
    chiSquare: float = field(metadata={"metadata": {
            "description": "Chi-square test for goodness of fit of this sample"
                           " to this 1000 Genomes Phase 3 population"
            },
        "required": True})
    KGSuperPopCategory: Optional[str] = field(metadata={
        "metadata": {"description": {"1K Super Population"}},
        "validate": validate.OneOf(kGSuperPopCategory.__members__.keys())
    })
    kGPopCategory: Optional[str] = field(metadata={
        "metadata": {"description": {"1K Super Population"}},
        "validate": validate.OneOf(KGPopCategory.__members__.keys())
    })




@dataclass
class InbreedingCoefficient:

    sampleId: str
    program: str
    version: str
    estimationMethod: str
    coefficient: float = field(
        metadata={"metadata": {"description": "Inbreeding coefficient"},
                  "validate": validate.Range(min=0, max=1)}
    )
    standardError: Optional[float] = field(default=None,
                                           metadata={"metadata": {
                                               "description": "Standard error of the Inbreeding coefficient"}})

@dataclass
class ConsentStatus:
    programmmeConsent: bool
    primaryFindingsConsent: bool = field(default=False)
    secondaryFindingsConsent: bool = field(default=False)
    carrierStatusConsent: bool = field(default=False)


@dataclass
class Ancestries:
    mothersEthnicOrigin: Optional[str] = field(default=None,
        metadata={"metadata": {"description": "Mother's Ethnic Origin"},
                  "validate": validate.OneOf(EthnicCategory.__members__)}
    )
    mothersOtherRelevantAncestry: Optional[str] = field(default=None)
    fathersEthnicOrigin: Optional[str] = field(default=None,
        metadata={"metadata": {"description": "Father's Ethnic Origin"},
                  "validate": validate.OneOf(EthnicCategory.__members__)}
    )
    fathersOtherRelevantAncestry: Optional[str] = field(default=None)
    chiSquare1KGenomesPhase3Pop = Optional[List[chiSquare1KGenomesPhase3Pop]]

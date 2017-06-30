from protocols.reports_3_0_0 import (
    Actions,
    ReportEvent,
    CancerSample,
    CalledGenotype,
    MatchedSamples,
    ReportedVariant,
    ReportEventCancer,
    ReportedStructuralVariant,
)
from protocols.reports_4_0_0 import (
    File,
    Tier,
    FileType,
    AlleleOrigin,
    FeatureTypes,
    ReportVersionControl,
    ReportedSomaticVariants,
    StructuralVariantFirstLevelType,
    ReportedSomaticStructuralVariants,
)
from protocols.participant_1_0_0 import CancerParticipant
from protocols.reports_4_0_0 import Actions as Actions_4_0_0
from protocols.reports_3_1_0 import ReportEvent as ReportEvent_3_1_0
from protocols.reports_3_1_0 import CancerSample as CancerSample_3_1_0
from protocols.reports_3_1_0 import CalledGenotype as CalledGenotype_3_1_0
from protocols.reports_3_1_0 import MatchedSamples as MatchedSamples_3_1_0
from protocols.reports_3_1_0 import ReportedVariant as ReportedVariant_3_1_0
from protocols.reports_4_0_0 import ReportEventCancer as ReportEventCancer_4_0_0
from protocols.reports_3_1_0 import ReportedStructuralVariant as ReportedStructuralVariant_3_1_0

TYPES_CONTAINED_WITHIN_ARRAYS = (
    Actions,
    ReportEvent,
    CancerSample,
    Actions_4_0_0,
    CalledGenotype,
    MatchedSamples,
    ReportedVariant,
    ReportEventCancer,
    ReportEvent_3_1_0,
    CancerSample_3_1_0,
    CalledGenotype_3_1_0,
    MatchedSamples_3_1_0,
    ReportedVariant_3_1_0,
    ReportEventCancer_4_0_0,
    ReportedStructuralVariant,
    ReportedStructuralVariant_3_1_0,
)


class MockTestObject(object):

    def __init__(self, object_type):
        self.object_type = object_type

    def set_embedded_objects(self, new_gel_object):
        for field_key in new_gel_object.schema.fields_dict.keys():
            if new_gel_object.isEmbeddedType(field_key):
                embedded_object = new_gel_object.getEmbeddedType(field_key)()
                schema_fields = embedded_object.schema.fields_dict.keys()
                embedded_objects_present = [embedded_object.isEmbeddedType(field) for field in schema_fields]
                embedded_object_types = [
                    embedded_object.getEmbeddedType(field) for field in schema_fields
                    if embedded_object.isEmbeddedType(field)
                ]
                if any(embedded_objects_present):
                    if not (len(embedded_object_types) == 1 and isinstance(embedded_object, embedded_object_types[0])):
                        self.set_embedded_objects(embedded_object)
                    else:
                        setattr(new_gel_object, field_key, embedded_object)
                if isinstance(embedded_object, TYPES_CONTAINED_WITHIN_ARRAYS):
                    setattr(new_gel_object, field_key, [embedded_object])
                else:
                    setattr(new_gel_object, field_key, embedded_object)

    def get_valid_empty_object(self):
        new_gel_object = self.object_type()
        self.set_embedded_objects(new_gel_object)
        return new_gel_object


def get_valid_empty_cancer_participant():
        new_participant = MockTestObject(object_type=CancerParticipant).get_valid_empty_object()
        new_participant.sex = 'M'
        new_participant.germlineSamples.labSampleId = 1
        new_participant.tumourSamples.tumourId = 1
        new_participant.tumourSamples.labSampleId = 1
        new_participant.readyForAnalysis = True
        new_participant.sex = 'UNKNOWN'

        matchedSample = new_participant.matchedSamples
        new_participant.matchedSamples = [matchedSample]

        germlineSample = new_participant.germlineSamples
        new_participant.germlineSamples = [germlineSample]

        tumourSample = new_participant.tumourSamples
        new_participant.tumourSamples = [tumourSample]

        if new_participant.validate(jsonDict=new_participant.toJsonDict()):
            return new_participant
        else:
            raise Exception("New CancerParticipant object is not valid")


def get_valid_empty_file(file_type=None):
    file_type = FileType.OTHER if file_type is None else file_type
    new_file = MockTestObject(object_type=File).get_valid_empty_object()
    new_file.fileType = file_type
    new_file.SampleId = ['']
    new_file.md5Sum.fileType = FileType.OTHER

    if new_file.validate(jsonDict=new_file.toJsonDict()):
        return new_file
    else:
        raise Exception("New File object is not valid")


def get_valid_empty_report_event_cancer():
    new_report_event = MockTestObject(object_type=ReportEventCancer_4_0_0).get_valid_empty_object()
    new_report_event.actions[0].variantActionable = False
    new_report_event.genomicFeatureCancer.featureType = FeatureTypes.Gene
    new_report_event.tier = Tier.NONE
    new_report_event.soTerms = [new_report_event.soTerms]

    if new_report_event.validate(jsonDict=new_report_event.toJsonDict()):
        return new_report_event
    else:
        raise Exception("New ReportEventCancer object is not valid")


def get_valid_empty_reported_somatic_variant():
    new_variant = MockTestObject(object_type=ReportedSomaticVariants).get_valid_empty_object()
    new_variant.reportedVariantCancer.position = 1
    new_variant.reportedVariantCancer.reportEvents[0] = get_valid_empty_report_event_cancer()
    new_variant.reportedVariantCancer.additionalTextualVariantAnnotations = {}
    new_variant.reportedVariantCancer.additionalNumericVariantAnnotations = {}
    new_variant.alleleOrigins = [AlleleOrigin.germline_variant]

    if new_variant.validate(jsonDict=new_variant.toJsonDict()):
        return new_variant
    else:
        raise Exception("New ReportedSomaticVariants object is not valid")


def get_valid_reported_somatic_structural_variant():
    new_variant = MockTestObject(object_type=ReportedSomaticStructuralVariants).get_valid_empty_object()
    new_variant.alleleOrigins = [AlleleOrigin.germline_variant]
    new_variant.reportedStructuralVariantCancer.additionalNumericVariantAnnotations = {}
    new_variant.reportedStructuralVariantCancer.additionalTextualVariantAnnotations = {}
    new_variant.reportedStructuralVariantCancer.start = 1
    new_variant.reportedStructuralVariantCancer.end = 2
    new_variant.reportedStructuralVariantCancer.type.firstLevelType = StructuralVariantFirstLevelType.DEL

    if new_variant.validate(new_variant.toJsonDict()):
        return new_variant
    else:
        raise Exception("New ReportedSomaticStructuralVariants object is not valid")


def get_valid_report_version_control():
    version_control = MockTestObject(object_type=ReportVersionControl).get_valid_empty_object()

    if version_control.validate(version_control.toJsonDict()):
        return version_control
    else:
        raise Exception("New ReportVersionControl object is not valid")


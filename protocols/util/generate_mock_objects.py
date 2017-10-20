from protocols import reports_2_1_0
from protocols import reports_3_0_0
from protocols import reports_3_1_0
from protocols import reports_4_0_0
from protocols import reports_4_2_0
from protocols import participant_1_0_0
from protocols import participant_1_0_4


class MockModelObject(object):

    def __init__(self, object_type):
        self.object_type = object_type

    @property
    def types_contained_within_array(self):
        return (
            reports_4_0_0.Sample,
            reports_4_2_0.Sample,
            reports_2_1_0.HpoTerm,
            reports_3_0_0.HpoTerm,
            reports_3_1_0.HpoTerm,
            reports_4_0_0.HpoTerm,
            reports_4_2_0.HpoTerm,
            reports_2_1_0.Actions,
            reports_3_0_0.Actions,
            reports_3_1_0.Actions,
            reports_4_0_0.Actions,
            reports_4_2_0.Action,
            reports_2_1_0.Disorder,
            reports_3_0_0.Disorder,
            reports_3_1_0.Disorder,
            reports_4_0_0.Disorder,
            reports_4_2_0.Disorder,
            reports_2_1_0.ReportEvent,
            reports_3_0_0.ReportEvent,
            reports_3_1_0.ReportEvent,
            reports_4_0_0.ReportEvent,
            reports_4_2_0.ReportEvent,
            reports_2_1_0.CancerSample,
            reports_3_0_0.CancerSample,
            reports_3_1_0.CancerSample,
            reports_2_1_0.AnalysisPanel,
            reports_3_0_0.AnalysisPanel,
            reports_3_1_0.AnalysisPanel,
            reports_4_0_0.AnalysisPanel,
            reports_4_2_0.AnalysisPanel,
            reports_2_1_0.RDParticipant,
            reports_3_0_0.RDParticipant,
            reports_3_1_0.RDParticipant,
            reports_2_1_0.CalledGenotype,
            reports_3_0_0.CalledGenotype,
            reports_3_1_0.CalledGenotype,
            reports_4_0_0.CalledGenotype,
            reports_4_2_0.CalledGenotype,
            reports_2_1_0.MatchedSamples,
            reports_3_0_0.MatchedSamples,
            reports_3_1_0.MatchedSamples,
            reports_4_0_0.PedigreeMember,
            reports_4_2_0.PedigreeMember,
            reports_2_1_0.ReportedVariant,
            reports_3_0_0.ReportedVariant,
            reports_3_1_0.ReportedVariant,
            reports_4_0_0.ReportedVariant,
            reports_4_2_0.ReportedVariant,
            reports_3_0_0.DiseasePenetrance,
            reports_3_1_0.DiseasePenetrance,
            reports_4_0_0.DiseasePenetrance,
            reports_4_2_0.DiseasePenetrance,
            reports_3_0_0.ReportEventCancer,
            reports_3_1_0.ReportEventCancer,
            reports_4_0_0.ReportEventCancer,
            reports_4_2_0.ReportEventCancer,
            reports_4_2_0.VariantCall,
            reports_3_0_0.VariantLevelQuestions,
            reports_3_1_0.VariantLevelQuestions,
            reports_4_0_0.VariantLevelQuestions,
            reports_4_2_0.VariantLevelQuestions,
            reports_2_1_0.ReportedSomaticVariants,
            reports_3_0_0.ReportedSomaticVariants,
            reports_3_1_0.ReportedSomaticVariants,
            reports_4_0_0.ReportedSomaticVariants,
            reports_2_1_0.ReportedStructuralVariant,
            reports_3_0_0.ReportedStructuralVariant,
            reports_3_1_0.ReportedStructuralVariant,
            reports_4_0_0.ReportedStructuralVariant,
            reports_4_2_0.ReportedStructuralVariant,
            reports_3_0_0.VariantGroupLevelQuestions,
            reports_3_1_0.VariantGroupLevelQuestions,
            reports_4_0_0.VariantGroupLevelQuestions,
            reports_4_2_0.VariantGroupLevelQuestions,
            reports_2_1_0.ChiSquare1KGenomesPhase3Pop,
            reports_3_0_0.ChiSquare1KGenomesPhase3Pop,
            reports_3_1_0.ChiSquare1KGenomesPhase3Pop,
            reports_4_0_0.ChiSquare1KGenomesPhase3Pop,
            reports_4_2_0.ChiSquare1KGenomesPhase3Pop,
            reports_2_1_0.ReportedSomaticStructuralVariants,
            reports_3_0_0.ReportedSomaticStructuralVariants,
            reports_3_1_0.ReportedSomaticStructuralVariants,
            reports_4_0_0.ReportedSomaticStructuralVariants,
        )

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
                if isinstance(embedded_object, self.types_contained_within_array):
                    setattr(new_gel_object, field_key, [embedded_object])
                else:
                    setattr(new_gel_object, field_key, embedded_object)

    def get_valid_empty_object(self):
        new_gel_object = self.object_type()
        self.set_embedded_objects(new_gel_object)
        return new_gel_object


def validate_object(object_to_validate, object_type):
    if object_to_validate.validate(jsonDict=object_to_validate.toJsonDict()):
        return object_to_validate
    else:
        raise Exception("New {object_type} object is not valid".format(object_type=object_type))


def get_valid_cancer_participant_1_0_0():
    object_type = participant_1_0_0.CancerParticipant
    new_participant = MockModelObject(object_type=object_type).get_valid_empty_object()
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

    return validate_object(object_to_validate=new_participant, object_type=object_type)


def get_valid_cancer_participant_1_0_4():
    object_type = participant_1_0_4.CancerParticipant
    new_participant = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_participant.sex = 'M'
    new_participant.germlineSamples.labSampleId = 1
    new_participant.tumourSamples.tumourId = '1'
    new_participant.tumourSamples.labSampleId = 1
    new_participant.readyForAnalysis = True
    new_participant.sex = 'UNKNOWN'
    new_participant.yearOfBirth = 1969

    matchedSample = new_participant.matchedSamples
    new_participant.matchedSamples = [matchedSample]

    germlineSample = new_participant.germlineSamples
    new_participant.germlineSamples = [germlineSample]

    tumourSample = new_participant.tumourSamples
    new_participant.tumourSamples = [tumourSample]

    return validate_object(object_to_validate=new_participant, object_type=object_type)


def get_valid_file_4_0_0(file_type=None):
    file_type = reports_4_0_0.FileType.OTHER if file_type is None else file_type
    new_file = MockModelObject(object_type=reports_4_0_0.File).get_valid_empty_object()
    new_file.fileType = file_type
    new_file.SampleId = ['']
    new_file.md5Sum.fileType = reports_4_0_0.FileType.OTHER

    return validate_object(object_to_validate=new_file, object_type=reports_4_0_0.File)


def get_valid_report_event_cancer_4_0_0():
    new_report_event = MockModelObject(object_type=reports_4_0_0.ReportEventCancer).get_valid_empty_object()
    new_report_event.actions[0].variantActionable = False
    new_report_event.actions[0].actionType = "diagnosis"
    new_report_event.genomicFeatureCancer.featureType = reports_4_0_0.FeatureTypes.Gene
    new_report_event.tier = reports_4_0_0.Tier.NONE
    new_report_event.soTerms = [new_report_event.soTerms]

    return validate_object(object_to_validate=new_report_event, object_type=reports_4_0_0.ReportEventCancer)


def get_valid_reported_somatic_variant_4_0_0():
    new_variant = MockModelObject(object_type=reports_4_0_0.ReportedSomaticVariants).get_valid_empty_object()
    new_variant.reportedVariantCancer.position = 1
    new_variant.reportedVariantCancer.reportEvents[0] = get_valid_report_event_cancer_4_0_0()
    new_variant.reportedVariantCancer.additionalTextualVariantAnnotations = {}
    new_variant.reportedVariantCancer.additionalNumericVariantAnnotations = {}
    new_variant.alleleOrigins = [reports_4_0_0.AlleleOrigin.germline_variant]

    return validate_object(object_to_validate=new_variant, object_type=reports_4_0_0.ReportedSomaticVariants)


def get_valid_reported_somatic_structural_variant_4_0_0():
    object_type = reports_4_0_0.ReportedSomaticStructuralVariants
    new_variant = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_variant.alleleOrigins = [reports_4_0_0.AlleleOrigin.germline_variant]
    new_variant.reportedStructuralVariantCancer.additionalNumericVariantAnnotations = {}
    new_variant.reportedStructuralVariantCancer.additionalTextualVariantAnnotations = {}
    new_variant.reportedStructuralVariantCancer.start = 1
    new_variant.reportedStructuralVariantCancer.end = 2
    new_variant.reportedStructuralVariantCancer.type.firstLevelType = reports_4_0_0.StructuralVariantFirstLevelType.DEL

    return validate_object(object_to_validate=new_variant, object_type=object_type)


def get_valid_report_version_control_4_0_0():
    version_control = MockModelObject(object_type=reports_4_0_0.ReportVersionControl).get_valid_empty_object()

    return validate_object(object_to_validate=version_control, object_type=reports_4_0_0.ReportVersionControl)


def get_valid_reported_somatic_structural_variant_3_0_0():
    object_type = reports_3_0_0.ReportedSomaticStructuralVariants
    new_variant = MockModelObject(object_type=object_type).get_valid_empty_object()

    new_variant.reportedStructuralVariantCancer.start = 1
    new_variant.reportedStructuralVariantCancer.end = 2
    new_variant.reportedStructuralVariantCancer.somaticOrGermline = reports_3_0_0.SomaticOrGermline.unknown
    new_variant.somaticOrGermline = reports_3_0_0.SomaticOrGermline.unknown

    return validate_object(object_to_validate=new_variant, object_type=object_type)

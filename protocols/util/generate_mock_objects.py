from copy import deepcopy

from protocols import reports_2_1_0
from protocols import reports_3_0_0
from protocols import reports_3_1_0
from protocols import reports_4_0_0
from protocols import reports_4_2_0_SNAPSHOT
from protocols import participant_1_0_0
from protocols import participant_1_0_3
from protocols import participant_1_0_4_SNAPSHOT
from protocols import cva_0_3_1
from protocols import cva_0_4_0_SNAPSHOT


class MockModelObject(object):

    def __init__(self, object_type):
        self.object_type = object_type

    @property
    def types_contained_within_array(self):
        return (
            reports_4_0_0.Sample,
            reports_4_2_0_SNAPSHOT.Sample,
            reports_2_1_0.HpoTerm,
            reports_3_0_0.HpoTerm,
            reports_3_1_0.HpoTerm,
            reports_4_0_0.HpoTerm,
            reports_4_2_0_SNAPSHOT.HpoTerm,
            reports_2_1_0.Actions,
            reports_3_0_0.Actions,
            reports_3_1_0.Actions,
            reports_4_0_0.Actions,
            reports_4_2_0_SNAPSHOT.Actions,
            reports_2_1_0.Disorder,
            reports_3_0_0.Disorder,
            reports_3_1_0.Disorder,
            reports_4_0_0.Disorder,
            reports_4_2_0_SNAPSHOT.Disorder,
            reports_2_1_0.ReportEvent,
            reports_3_0_0.ReportEvent,
            reports_3_1_0.ReportEvent,
            reports_4_0_0.ReportEvent,
            reports_4_2_0_SNAPSHOT.ReportEvent,
            reports_2_1_0.CancerSample,
            reports_3_0_0.CancerSample,
            reports_3_1_0.CancerSample,
            reports_2_1_0.AnalysisPanel,
            reports_3_0_0.AnalysisPanel,
            reports_3_1_0.AnalysisPanel,
            reports_4_0_0.AnalysisPanel,
            reports_4_2_0_SNAPSHOT.AnalysisPanel,
            reports_2_1_0.RDParticipant,
            reports_3_0_0.RDParticipant,
            reports_3_1_0.RDParticipant,
            reports_2_1_0.CalledGenotype,
            reports_3_0_0.CalledGenotype,
            reports_3_1_0.CalledGenotype,
            reports_4_0_0.CalledGenotype,
            reports_4_2_0_SNAPSHOT.CalledGenotype,
            reports_2_1_0.MatchedSamples,
            reports_3_0_0.MatchedSamples,
            reports_3_1_0.MatchedSamples,
            reports_4_0_0.PedigreeMember,
            reports_4_2_0_SNAPSHOT.PedigreeMember,
            reports_2_1_0.ReportedVariant,
            reports_3_0_0.ReportedVariant,
            reports_3_1_0.ReportedVariant,
            reports_4_0_0.ReportedVariant,
            reports_4_2_0_SNAPSHOT.ReportedVariant,
            reports_3_0_0.DiseasePenetrance,
            reports_3_1_0.DiseasePenetrance,
            reports_4_0_0.DiseasePenetrance,
            reports_4_2_0_SNAPSHOT.DiseasePenetrance,
            reports_3_0_0.ReportEventCancer,
            reports_3_1_0.ReportEventCancer,
            reports_4_0_0.ReportEventCancer,
            reports_4_2_0_SNAPSHOT.ReportEventCancer,
            reports_4_2_0_SNAPSHOT.VariantCall,
            reports_3_0_0.VariantLevelQuestions,
            reports_3_1_0.VariantLevelQuestions,
            reports_4_0_0.VariantLevelQuestions,
            reports_4_2_0_SNAPSHOT.VariantLevelQuestions,
            reports_2_1_0.ReportedSomaticVariants,
            reports_3_0_0.ReportedSomaticVariants,
            reports_3_1_0.ReportedSomaticVariants,
            reports_4_0_0.ReportedSomaticVariants,
            reports_4_2_0_SNAPSHOT.ReportedSomaticVariants,
            reports_2_1_0.ReportedStructuralVariant,
            reports_3_0_0.ReportedStructuralVariant,
            reports_3_1_0.ReportedStructuralVariant,
            reports_4_0_0.ReportedStructuralVariant,
            reports_4_2_0_SNAPSHOT.ReportedStructuralVariant,
            reports_3_0_0.VariantGroupLevelQuestions,
            reports_3_1_0.VariantGroupLevelQuestions,
            reports_4_0_0.VariantGroupLevelQuestions,
            reports_4_2_0_SNAPSHOT.VariantGroupLevelQuestions,
            reports_2_1_0.ChiSquare1KGenomesPhase3Pop,
            reports_3_0_0.ChiSquare1KGenomesPhase3Pop,
            reports_3_1_0.ChiSquare1KGenomesPhase3Pop,
            reports_4_0_0.ChiSquare1KGenomesPhase3Pop,
            reports_4_2_0_SNAPSHOT.ChiSquare1KGenomesPhase3Pop,
            reports_2_1_0.ReportedSomaticStructuralVariants,
            reports_3_0_0.ReportedSomaticStructuralVariants,
            reports_3_1_0.ReportedSomaticStructuralVariants,
            reports_4_0_0.ReportedSomaticStructuralVariants,
            reports_4_2_0_SNAPSHOT.ReportedSomaticStructuralVariants,
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


def get_valid_cancer_participant_2_1_0():
    object_type = reports_2_1_0.CancerParticipant
    participant = MockModelObject(object_type=object_type).get_valid_empty_object()

    participant.cancerSamples[0].sampleType = reports_2_1_0.SampleType.tumor
    participant.cancerSamples[0].labId = '1'

    additional_sample = deepcopy(participant.cancerSamples[0])
    participant.cancerSamples.append(additional_sample)
    participant.cancerSamples[1].sampleType = reports_2_1_0.SampleType.germline
    participant.cancerSamples[1].labId = '2'

    return validate_object(object_to_validate=participant, object_type=object_type)


def get_valid_cancer_participant_3_0_0():
    participant = MockModelObject(object_type=reports_3_0_0.CancerParticipant).get_valid_empty_object()
    participant.cancerDemographics.sex = 'M'
    participant.cancerSamples[0].sampleType = 'tumor'
    participant.cancerSamples[0].labId = '1'
    additional_sample = deepcopy(participant.cancerSamples[0])
    participant.cancerSamples.append(additional_sample)
    participant.cancerSamples[1].sampleType = 'germline'
    participant.cancerSamples[1].labId = '2'

    return validate_object(object_to_validate=participant, object_type=reports_3_0_0.CancerParticipant)


def get_valid_cancer_participant_3_1_0():
    object_type = reports_3_1_0.CancerParticipant
    participant = MockModelObject(object_type=object_type).get_valid_empty_object()

    participant.cancerSamples[0].sampleType = reports_3_1_0.SampleType.tumor
    participant.cancerSamples[0].labId = '1'

    additional_sample = deepcopy(participant.cancerSamples[0])
    participant.cancerSamples.append(additional_sample)
    participant.cancerSamples[1].sampleType = reports_3_1_0.SampleType.germline
    participant.cancerSamples[1].labId = '2'

    return validate_object(object_to_validate=participant, object_type=object_type)


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


def get_valid_cancer_participant_1_0_3():
    object_type = participant_1_0_3.CancerParticipant
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


def get_valid_cancer_participant_1_0_4_SNAPSHOT():
    object_type = participant_1_0_4_SNAPSHOT.CancerParticipant
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
    new_report_event.genomicFeatureCancer.featureType = reports_4_0_0.FeatureTypes.Gene
    new_report_event.tier = reports_4_0_0.Tier.NONE
    new_report_event.soTerms = [new_report_event.soTerms]

    return validate_object(object_to_validate=new_report_event, object_type=reports_4_0_0.ReportEventCancer)


def get_valid_reported_variant_cancer_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.ReportedVariantCancer
    reported_variant_cancer = MockModelObject(object_type=object_type).get_valid_empty_object()
    reported_variant_cancer.position = 1
    reported_variant_cancer.reportEvents[0] = get_valid_report_event_cancer_4_2_0_SNAPSHOT()
    reported_variant_cancer.additionalTextualVariantAnnotations = {}
    reported_variant_cancer.additionalNumericVariantAnnotations = {}

    return validate_object(object_to_validate=reported_variant_cancer, object_type=object_type)


def get_valid_report_event_cancer_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.ReportEventCancer
    new_report_event = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_report_event.actions[0].variantActionable = False
    new_report_event.genomicFeatureCancer.featureType = reports_4_2_0_SNAPSHOT.FeatureTypes.Gene
    new_report_event.tier = reports_4_2_0_SNAPSHOT.Tier.NONE
    new_report_event.soTerms = [new_report_event.soTerms]

    return validate_object(object_to_validate=new_report_event, object_type=object_type)


def get_valid_reported_somatic_variant_4_0_0():
    new_variant = MockModelObject(object_type=reports_4_0_0.ReportedSomaticVariants).get_valid_empty_object()
    new_variant.reportedVariantCancer.position = 1
    new_variant.reportedVariantCancer.reportEvents[0] = get_valid_report_event_cancer_4_0_0()
    new_variant.reportedVariantCancer.additionalTextualVariantAnnotations = {}
    new_variant.reportedVariantCancer.additionalNumericVariantAnnotations = {}
    new_variant.alleleOrigins = [reports_4_0_0.AlleleOrigin.germline_variant]

    return validate_object(object_to_validate=new_variant, object_type=reports_4_0_0.ReportedSomaticVariants)


def get_valid_reported_somatic_variant_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.ReportedSomaticVariants
    new_variant = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_variant.reportedVariantCancer = get_valid_reported_variant_cancer_4_2_0_SNAPSHOT()
    new_variant.alleleOrigins = [reports_4_2_0_SNAPSHOT.AlleleOrigin.germline_variant]

    return validate_object(object_to_validate=new_variant, object_type=object_type)


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


def get_valid_reported_somatic_structural_variant_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.ReportedSomaticStructuralVariants
    new_variant = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_variant.alleleOrigins = [reports_4_2_0_SNAPSHOT.AlleleOrigin.germline_variant]
    new_variant.reportedStructuralVariantCancer.additionalNumericVariantAnnotations = {}
    new_variant.reportedStructuralVariantCancer.additionalTextualVariantAnnotations = {}
    new_variant.reportedStructuralVariantCancer.start = 1
    new_variant.reportedStructuralVariantCancer.end = 2
    firstLevelType = reports_4_2_0_SNAPSHOT.StructuralVariantFirstLevelType.DEL
    new_variant.reportedStructuralVariantCancer.type.firstLevelType = firstLevelType

    return validate_object(object_to_validate=new_variant, object_type=object_type)


def get_valid_report_version_control_4_0_0():
    version_control = MockModelObject(object_type=reports_4_0_0.ReportVersionControl).get_valid_empty_object()

    return validate_object(object_to_validate=version_control, object_type=reports_4_0_0.ReportVersionControl)


def get_valid_called_genotype_3_0_0():
    new_cg = MockModelObject(object_type=reports_3_0_0.CalledGenotype).get_valid_empty_object()
    new_cg.genotype = reports_3_0_0.Zygosity.unk

    return validate_object(object_to_validate=new_cg, object_type=reports_3_0_0.CalledGenotype)


def get_valid_report_event_3_0_0():
    new_report_event = MockModelObject(object_type=reports_3_0_0.ReportEvent).get_valid_empty_object()
    new_report_event.genomicFeature.featureType = 'RegulatoryRegion'
    new_report_event.modeOfInheritance = 'monoallelic'
    new_report_event.penetrance = 'incomplete'
    new_report_event.score = 0.0
    new_report_event.vendorSpecificScores = {}
    new_report_event.variantClassification = 'BENIGN'
    new_report_event.tier = 'NONE'
    new_report_event.panelVersion = ''
    new_report_event.panelName = ''
    new_report_event.genomicFeature.HGNC = ''
    new_report_event.genomicFeature.other_ids = {}

    return validate_object(object_to_validate=new_report_event, object_type=reports_3_0_0.ReportEvent)


def get_valid_reported_structural_variant_3_0_0():
    new_rsv = MockModelObject(object_type=reports_3_0_0.ReportedStructuralVariant).get_valid_empty_object()
    new_rsv.calledGenotypes[0] = get_valid_called_genotype_3_0_0()
    new_rsv.reportEvents[0] = get_valid_report_event_3_0_0()
    new_rsv.start, new_rsv.end = 1, 2
    new_rsv.evidenceIds = {}
    new_rsv.comments = ['']
    new_rsv.additionalTextualVariantAnnotations = {}
    new_rsv.additionalNumericVariantAnnotations = {}

    return validate_object(object_to_validate=new_rsv, object_type=reports_3_0_0.ReportedStructuralVariant)


def get_valid_reported_variant_3_0_0():
    new_rv = MockModelObject(object_type=reports_3_0_0.ReportedVariant).get_valid_empty_object()
    new_rv.calledGenotypes[0] = get_valid_called_genotype_3_0_0()
    new_rv.reportEvents[0] = get_valid_report_event_3_0_0()
    new_rv.position = 0
    new_rv.evidenceIds = {}
    new_rv.comments = ['']
    new_rv.dbSNPid = ''
    new_rv.additionalNumericVariantAnnotations = {}
    new_rv.additionalTextualVariantAnnotations = {}

    return validate_object(object_to_validate=new_rv, object_type=reports_3_0_0.ReportedVariant)


def get_valid_interpreted_genome_rd_3_0_0():
    object_type = reports_3_0_0.InterpretedGenomeRD
    new_ig_rd = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_ig_rd.softwareVersions = {}
    new_ig_rd.referenceDatabasesVersions = {}
    new_ig_rd.penetrance = reports_3_0_0.Penetrance.complete
    new_ig_rd.modeOfInheritance = reports_3_0_0.ReportedModeOfInheritance.unknown
    new_ig_rd.reportedVariants[0] = get_valid_reported_variant_3_0_0()
    new_ig_rd.reportedStructuralVariants[0] = get_valid_reported_structural_variant_3_0_0()

    return validate_object(object_to_validate=new_ig_rd, object_type=object_type)


def get_valid_interpreted_genome_rd_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.InterpretedGenomeRD
    new_ig_rd = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_ig_rd.softwareVersions = {}
    new_ig_rd.referenceDatabasesVersions = {}
    new_ig_rd.penetrance = reports_4_2_0_SNAPSHOT.Penetrance.complete
    new_ig_rd.modeOfInheritance = reports_4_2_0_SNAPSHOT.ReportedModeOfInheritance.unknown
    new_ig_rd.reportedVariants[0] = get_valid_reported_variant_4_2_0_SNAPSHOT()
    new_ig_rd.reportedStructuralVariants[0] = get_valid_reported_structural_variant_4_2_0_SNAPSHOT()

    return validate_object(object_to_validate=new_ig_rd, object_type=object_type)


def get_valid_called_genotype_3_1_0():
    object_type = reports_3_1_0.CalledGenotype
    new_cg = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cg.genotype = reports_3_1_0.Zygosity.unk

    return validate_object(object_to_validate=new_cg, object_type=object_type)


def get_valid_report_event_3_1_0():
    object_type = reports_3_1_0.ReportEvent
    new_report_event = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_report_event.score = 0.0
    new_report_event.penetrance = reports_3_1_0.Penetrance.complete
    new_report_event.modeOfInheritance = reports_3_1_0.ReportedModeOfInheritance.unknown
    new_report_event.genomicFeature.featureType = reports_3_1_0.FeatureTypes.RegulatoryRegion

    return validate_object(object_to_validate=new_report_event, object_type=object_type)


def get_valid_reported_variant_3_1_0():
    object_type = reports_3_1_0.ReportedVariant
    new_rv = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_rv.calledGenotypes[0] = get_valid_called_genotype_3_1_0()
    new_rv.reportEvents[0] = get_valid_report_event_3_1_0()
    new_rv.position = 0

    return validate_object(object_to_validate=new_rv, object_type=object_type)


def get_valid_reported_structural_variant_3_1_0():
    object_type = reports_3_1_0.ReportedStructuralVariant
    new_rsv = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_rsv.calledGenotypes[0] = get_valid_called_genotype_3_1_0()
    new_rsv.reportEvents[0] = get_valid_report_event_3_1_0()
    new_rsv.start, new_rsv.end = 1, 2

    return validate_object(object_to_validate=new_rsv, object_type=object_type)


def get_valid_interpreted_genome_rd_3_1_0():
    object_type = reports_3_1_0.InterpretedGenomeRD
    new_ig_rd = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_ig_rd.softwareVersions = {}
    new_ig_rd.referenceDatabasesVersions = {}

    new_ig_rd.reportedVariants[0] = get_valid_reported_variant_3_1_0()
    new_ig_rd.reportedStructuralVariants[0] = get_valid_reported_structural_variant_3_1_0()

    return validate_object(object_to_validate=new_ig_rd, object_type=object_type)


def get_valid_called_genotype_4_0_0():
    object_type = reports_4_0_0.CalledGenotype
    new_cg = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cg.genotype = reports_4_0_0.Zygosity.unk

    return validate_object(object_to_validate=new_cg, object_type=object_type)


def get_valid_called_genotype_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.CalledGenotype
    new_cg = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cg.genotype = reports_4_2_0_SNAPSHOT.Zygosity.unk

    return validate_object(object_to_validate=new_cg, object_type=object_type)


def get_valid_report_event_4_0_0():
    object_type = reports_4_0_0.ReportEvent
    new_report_event = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_report_event.score = 0.0
    new_report_event.penetrance = reports_4_0_0.Penetrance.complete
    new_report_event.modeOfInheritance = reports_4_0_0.ReportedModeOfInheritance.unknown
    new_report_event.genomicFeature.featureType = reports_4_0_0.FeatureTypes.RegulatoryRegion

    return validate_object(object_to_validate=new_report_event, object_type=object_type)


def get_valid_report_event_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.ReportEvent
    new_report_event = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_report_event.score = 0.0
    new_report_event.penetrance = reports_4_2_0_SNAPSHOT.Penetrance.complete
    new_report_event.modeOfInheritance = reports_4_2_0_SNAPSHOT.ReportedModeOfInheritance.unknown
    new_report_event.genomicFeature.featureType = reports_4_2_0_SNAPSHOT.FeatureTypes.RegulatoryRegion

    return validate_object(object_to_validate=new_report_event, object_type=object_type)


def get_valid_reported_variant_4_0_0():
    object_type = reports_4_0_0.ReportedVariant
    new_rv = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_rv.calledGenotypes[0] = get_valid_called_genotype_4_0_0()
    new_rv.reportEvents[0] = get_valid_report_event_4_0_0()
    new_rv.position = 0
    new_rv.evidenceIds = {}
    new_rv.comments = ['']
    new_rv.dbSNPid = ''
    new_rv.additionalNumericVariantAnnotations = {}
    new_rv.additionalTextualVariantAnnotations = {}

    return validate_object(object_to_validate=new_rv, object_type=object_type)


def get_valid_reported_variant_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.ReportedVariant
    new_rv = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_rv.calledGenotypes[0] = get_valid_called_genotype_4_2_0_SNAPSHOT()
    new_rv.reportEvents[0] = get_valid_report_event_4_2_0_SNAPSHOT()
    new_rv.position = 0
    new_rv.evidenceIds = {}
    new_rv.comments = ['']
    new_rv.dbSnpId = ''
    new_rv.additionalNumericVariantAnnotations = {}
    new_rv.additionalTextualVariantAnnotations = {}

    return validate_object(object_to_validate=new_rv, object_type=object_type)


def get_valid_reported_structural_variant_4_0_0():
    object_type = reports_4_0_0.ReportedStructuralVariant
    new_rsv = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_rsv.calledGenotypes[0] = get_valid_called_genotype_4_0_0()
    new_rsv.reportEvents[0] = get_valid_report_event_4_0_0()
    new_rsv.start, new_rsv.end = 1, 2

    return validate_object(object_to_validate=new_rsv, object_type=object_type)

def get_valid_reported_structural_variant_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.ReportedStructuralVariant
    new_rsv = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_rsv.calledGenotypes[0] = get_valid_called_genotype_4_2_0_SNAPSHOT()
    new_rsv.reportEvents[0] = get_valid_report_event_4_2_0_SNAPSHOT()
    new_rsv.start, new_rsv.end = 1, 2

    return validate_object(object_to_validate=new_rsv, object_type=object_type)


def get_valid_interpreted_genome_rd_4_0_0():
    object_type = reports_4_0_0.InterpretedGenomeRD
    new_ig_rd = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_ig_rd.softwareVersions = {}
    new_ig_rd.referenceDatabasesVersions = {}
    new_ig_rd.reportedVariants = [get_valid_reported_variant_4_0_0()]
    new_ig_rd.reportedStructuralVariants = [get_valid_reported_structural_variant_4_0_0()]

    return validate_object(object_to_validate=new_ig_rd, object_type=object_type)


def get_valid_interpretation_request_rd_3_0_0():
    new_ir_rd = MockModelObject(object_type=reports_3_0_0.InterpretationRequestRD).get_valid_empty_object()

    new_ir_rd.workspace = ['']
    new_ir_rd.pedigreeDiagram.fileType = reports_3_0_0.FileType.OTHER

    new_ir_rd.BAMs = [new_ir_rd.BAMs]
    new_ir_rd.BAMs[0].fileType = reports_3_0_0.FileType.BAM

    new_ir_rd.VCFs = [new_ir_rd.VCFs]
    new_ir_rd.VCFs[0].fileType = reports_3_0_0.FileType.VCF_CNV

    new_ir_rd.annotationFile.fileType = reports_3_0_0.FileType.ANN

    new_ir_rd.bigWigs = [new_ir_rd.bigWigs]
    new_ir_rd.bigWigs[0].fileType = reports_3_0_0.FileType.BigWig

    new_ir_rd.pedigree.participants[0].sex = "unknown"
    new_ir_rd.pedigree.participants[0].pedigreeId = 42
    new_ir_rd.pedigree.participants[0].lifeStatus = "alive"
    new_ir_rd.pedigree.participants[0].isProband = True
    new_ir_rd.pedigree.participants[0].inbreedingCoefficient.coefficient = 0.0
    new_ir_rd.pedigree.participants[0].consanguineousParents = reports_3_0_0.TernaryOption.unknown
    new_ir_rd.pedigree.participants[0].ancestries.chiSquare1KGenomesPhase3Pop[0].chiSquare = 0.0
    new_ir_rd.pedigree.participants[0].ancestries.chiSquare1KGenomesPhase3Pop[0].kGSuperPopCategory = "AFR"
    new_ir_rd.pedigree.participants[0].affectionStatus = "unaffected"
    new_ir_rd.pedigree.participants[0].adoptedStatus = "not_adopted"
    new_ir_rd.pedigree.diseasePenetrances[0].penetrance = 'incomplete'

    # TODO(Greg): Potentially implement get_called_genotype to help
    # TODO(Greg): either that or actually read the schema... perhaps this will be a better idea
    # TODO(Greg): in the long run

    new_ir_rd.InterpretationRequestVersion = 1
    # TODO(Greg): TieredVariants is a list of ReportedVariant objects
    # TODO(Greg): In the functionality above we need to make sure these values are set by default
    # TODO(Greg): for objects of these types
    new_ir_rd.TieredVariants[0].calledGenotypes[0].genotype = "unk"
    new_ir_rd.TieredVariants[0].position = 0

    # TODO(Greg): Same as the TODO above, but for ReportEvent objects
    new_ir_rd.TieredVariants[0].reportEvents[0] = get_valid_report_event_3_0_0()

    return validate_object(object_to_validate=new_ir_rd, object_type=reports_3_0_0.InterpretationRequestRD)


def get_valid_rd_exit_questionnaire_3_0_0():
    new_rd_eq = MockModelObject(object_type=reports_3_0_0.RareDiseaseExitQuestionnaire).get_valid_empty_object()

    classification = reports_3_0_0.ACMGClassification.not_assessed
    new_rd_eq.variantGroupLevelQuestions[0].variantLevelQuestions[0].acmgClassification = classification
    question = reports_3_0_0.ReportingQuestion.na
    new_rd_eq.variantGroupLevelQuestions[0].variantLevelQuestions[0].reportingQuestion = question
    outcome = reports_3_0_0.ConfirmationOutcome.na
    new_rd_eq.variantGroupLevelQuestions[0].variantLevelQuestions[0].confirmationOutcome = outcome
    decision = reports_3_0_0.ConfirmationDecision.na
    new_rd_eq.variantGroupLevelQuestions[0].variantLevelQuestions[0].confirmationDecision = decision
    new_rd_eq.variantGroupLevelQuestions[0].phenotypesSolved = reports_3_0_0.PhenotypesSolved.unknown
    new_rd_eq.variantGroupLevelQuestions[0].clinicalUtility = [reports_3_0_0.ClinicalUtility.unknown]
    new_rd_eq.variantGroupLevelQuestions[0].actionability = reports_3_0_0.Actionability.na
    new_rd_eq.variantGroupLevelQuestions[0].variant_group = 1

    new_rd_eq.familyLevelQuestions.segregationQuestion = reports_3_0_0.SegregationQuestion.no
    new_rd_eq.familyLevelQuestions.caseSolvedFamily = reports_3_0_0.CaseSolvedFamily.unknown

    return validate_object(object_to_validate=new_rd_eq, object_type=reports_3_0_0.RareDiseaseExitQuestionnaire)


def get_valid_rd_exit_questionnaire_3_1_0():
    object_type = reports_3_1_0.RareDiseaseExitQuestionnaire
    new_rd_eq = MockModelObject(object_type=object_type).get_valid_empty_object()

    classification = reports_3_1_0.ACMGClassification.not_assessed
    new_rd_eq.variantGroupLevelQuestions[0].variantLevelQuestions[0].acmgClassification = classification
    question = reports_3_1_0.ReportingQuestion.na
    new_rd_eq.variantGroupLevelQuestions[0].variantLevelQuestions[0].reportingQuestion = question
    outcome = reports_3_1_0.ConfirmationOutcome.na
    new_rd_eq.variantGroupLevelQuestions[0].variantLevelQuestions[0].confirmationOutcome = outcome
    decision = reports_3_1_0.ConfirmationDecision.na
    new_rd_eq.variantGroupLevelQuestions[0].variantLevelQuestions[0].confirmationDecision = decision
    new_rd_eq.variantGroupLevelQuestions[0].phenotypesSolved = reports_3_1_0.PhenotypesSolved.unknown
    new_rd_eq.variantGroupLevelQuestions[0].clinicalUtility = [reports_3_1_0.ClinicalUtility.unknown]
    new_rd_eq.variantGroupLevelQuestions[0].actionability = reports_3_1_0.Actionability.na
    new_rd_eq.variantGroupLevelQuestions[0].variantGroup = 1

    new_rd_eq.familyLevelQuestions.segregationQuestion = reports_3_1_0.SegregationQuestion.no
    new_rd_eq.familyLevelQuestions.caseSolvedFamily = reports_3_1_0.CaseSolvedFamily.unknown

    return validate_object(object_to_validate=new_rd_eq, object_type=object_type)


def get_valid_rd_exit_questionnaire_4_0_0():
    object_type = reports_4_0_0.RareDiseaseExitQuestionnaire
    new_rd_eq = MockModelObject(object_type=object_type).get_valid_empty_object()

    classification = reports_4_0_0.ACMGClassification.not_assessed
    new_rd_eq.variantGroupLevelQuestions[0].variantLevelQuestions[0].acmgClassification = classification
    question = reports_4_0_0.ReportingQuestion.na
    new_rd_eq.variantGroupLevelQuestions[0].variantLevelQuestions[0].reportingQuestion = question
    outcome = reports_4_0_0.ConfirmationOutcome.na
    new_rd_eq.variantGroupLevelQuestions[0].variantLevelQuestions[0].confirmationOutcome = outcome
    decision = reports_4_0_0.ConfirmationDecision.na
    new_rd_eq.variantGroupLevelQuestions[0].variantLevelQuestions[0].confirmationDecision = decision
    new_rd_eq.variantGroupLevelQuestions[0].phenotypesSolved = reports_4_0_0.PhenotypesSolved.unknown
    new_rd_eq.variantGroupLevelQuestions[0].clinicalUtility = [reports_4_0_0.ClinicalUtility.unknown]
    new_rd_eq.variantGroupLevelQuestions[0].actionability = reports_4_0_0.Actionability.na
    new_rd_eq.variantGroupLevelQuestions[0].variantGroup = 1

    new_rd_eq.familyLevelQuestions.segregationQuestion = reports_4_0_0.SegregationQuestion.no
    new_rd_eq.familyLevelQuestions.caseSolvedFamily = reports_4_0_0.CaseSolvedFamily.unknown

    return validate_object(object_to_validate=new_rd_eq, object_type=object_type)


def get_valid_reported_somatic_structural_variant_3_0_0():
    object_type = reports_3_0_0.ReportedSomaticStructuralVariants
    new_variant = MockModelObject(object_type=object_type).get_valid_empty_object()

    new_variant.reportedStructuralVariantCancer.start = 1
    new_variant.reportedStructuralVariantCancer.end = 2
    new_variant.reportedStructuralVariantCancer.somaticOrGermline = reports_3_0_0.SomaticOrGermline.unknown
    new_variant.somaticOrGermline = reports_3_0_0.SomaticOrGermline.unknown

    return validate_object(object_to_validate=new_variant, object_type=object_type)


def get_valid_report_event_cancer_3_0_0():
    new_report_event = MockModelObject(object_type=reports_3_0_0.ReportEventCancer).get_valid_empty_object()
    new_report_event.actions[0].variantActionable = False
    new_report_event.genomicFeatureCancer.featureType = reports_3_0_0.FeatureTypes.Gene
    new_report_event.tier = reports_3_0_0.Tier.NONE
    new_report_event.soTerms = ['']
    new_report_event.soNames = ['']

    return validate_object(object_to_validate=new_report_event, object_type=reports_3_0_0.ReportEventCancer)


def get_valid_reported_somatic_variant_3_0_0():
    object_type = reports_3_0_0.ReportedSomaticVariants
    new_variant = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_variant.somaticOrGermline = reports_3_0_0.SomaticOrGermline.unknown
    new_variant.reportedVariantCancer.reportEvents[0] = get_valid_report_event_cancer_3_0_0()
    new_variant.reportedVariantCancer.position = 0
    new_variant.somaticOrGermline = reports_3_0_0.SomaticOrGermline.somatic

    return validate_object(object_to_validate=new_variant, object_type=object_type)


def get_valid_cancer_interpretation_request_3_0_0():
    new_cir = MockModelObject(object_type=reports_3_0_0.CancerInterpretationRequest).get_valid_empty_object()
    new_cir.workspace = ['']
    new_cir.BAMs = [new_cir.BAMs]
    new_cir.BAMs[0].fileType = reports_3_0_0.FileType.BAM
    new_cir.bigWigs = [new_cir.bigWigs]
    new_cir.bigWigs[0].fileType = reports_3_0_0.FileType.BigWig
    new_cir.VCFs = [new_cir.VCFs]
    new_cir.VCFs[0].fileType = reports_3_0_0.FileType.VCF_small
    new_cir.cancerParticipant.cancerSamples[0].sampleType = reports_3_0_0.SampleType.tumor
    new_cir.annotationFile.fileType = reports_3_0_0.FileType.ANN
    new_cir.structuralTieredVariants[0] = get_valid_reported_somatic_structural_variant_3_0_0()
    new_cir.TieredVariants[0] = get_valid_reported_somatic_variant_3_0_0()
    new_cir.reportVersion = 1

    return validate_object(object_to_validate=new_cir, object_type=reports_3_0_0.CancerInterpretationRequest)


def get_valid_clinical_report_rd_2_1_0():
    object_type = reports_2_1_0.ClinicalReportRD
    new_cr_rd = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cr_rd.candidateVariants[0] = get_valid_reported_variant_2_1_0()
    new_cr_rd.candidateStructuralVariants[0] = get_valid_reported_structural_variant_2_1_0()
    new_cr_rd.softwareVersions = {'this': 'that'}
    new_cr_rd.referenceDatabasesVersions = {'this': 'that'}

    return validate_object(object_to_validate=new_cr_rd, object_type=object_type)


def get_valid_clinical_report_rd_3_0_0():
    object_type = reports_3_0_0.ClinicalReportRD
    new_cr_rd = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cr_rd.candidateVariants[0] = get_valid_reported_variant_3_0_0()
    new_cr_rd.candidateStructuralVariants[0] = get_valid_reported_structural_variant_3_0_0()
    new_cr_rd.softwareVersions = {'this': 'that'}
    new_cr_rd.referenceDatabasesVersions = {'this': 'that'}
    new_cr_rd.additionalAnalysisPanels = [new_cr_rd.additionalAnalysisPanels]

    return validate_object(object_to_validate=new_cr_rd, object_type=object_type)


def get_valid_clinical_report_rd_3_1_0():
    object_type = reports_3_1_0.ClinicalReportRD
    new_cr_rd = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cr_rd.candidateVariants[0] = get_valid_reported_variant_3_1_0()
    new_cr_rd.candidateStructuralVariants[0] = get_valid_reported_structural_variant_3_1_0()
    new_cr_rd.softwareVersions = {'this': 'that'}
    new_cr_rd.referenceDatabasesVersions = {'this': 'that'}
    new_cr_rd.additionalAnalysisPanels = [new_cr_rd.additionalAnalysisPanels]

    return validate_object(object_to_validate=new_cr_rd, object_type=object_type)


def get_valid_clinical_report_rd_4_0_0():
    object_type = reports_4_0_0.ClinicalReportRD
    new_cr_rd = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cr_rd.candidateVariants[0] = get_valid_reported_variant_4_0_0()
    new_cr_rd.candidateStructuralVariants[0] = get_valid_reported_structural_variant_4_0_0()
    new_cr_rd.softwareVersions = {'this': 'that'}
    new_cr_rd.referenceDatabasesVersions = {'this': 'that'}
    new_cr_rd.additionalAnalysisPanels = [new_cr_rd.additionalAnalysisPanels]

    return validate_object(object_to_validate=new_cr_rd, object_type=object_type)


def get_valid_clinical_report_rd_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.ClinicalReportRD
    new_cr_rd = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cr_rd.candidateVariants[0] = get_valid_reported_variant_4_2_0_SNAPSHOT()
    new_cr_rd.candidateStructuralVariants[0] = get_valid_reported_structural_variant_4_2_0_SNAPSHOT()
    new_cr_rd.softwareVersions = {'this': 'that'}
    new_cr_rd.referenceDatabasesVersions = {'this': 'that'}
    new_cr_rd.additionalAnalysisPanels = [new_cr_rd.additionalAnalysisPanels]

    return validate_object(object_to_validate=new_cr_rd, object_type=object_type)


def get_valid_cancer_interpreted_genome_3_0_0():
    object_type = reports_3_0_0.CancerInterpretedGenome
    new_cig = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cig.softwareVersions = {'this': 'that'}
    new_cig.referenceDatabasesVersions = {'this': 'that'}
    new_cig.reportedStructuralVariants[0] = get_valid_reported_somatic_structural_variant_3_0_0()
    new_cig.reportedVariants[0] = get_valid_reported_somatic_variant_3_0_0()

    return validate_object(object_to_validate=new_cig, object_type=object_type)


def get_valid_reported_somatic_structural_variant_3_1_0():
    object_type = reports_3_1_0.ReportedSomaticStructuralVariants
    new_variant = MockModelObject(object_type=object_type).get_valid_empty_object()

    new_variant.reportedStructuralVariantCancer.start = 1
    new_variant.reportedStructuralVariantCancer.end = 2
    new_variant.reportedStructuralVariantCancer.somaticOrGermline = reports_3_1_0.SomaticOrGermline.unknown
    new_variant.somaticOrGermline = reports_3_1_0.SomaticOrGermline.unknown

    return validate_object(object_to_validate=new_variant, object_type=object_type)


def get_valid_report_event_cancer_3_1_0():
    object_type = reports_3_1_0.ReportEventCancer
    new_report_event = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_report_event.actions[0].variantActionable = False
    new_report_event.genomicFeatureCancer.featureType = reports_3_1_0.FeatureTypes.Gene
    new_report_event.tier = reports_3_1_0.Tier.NONE
    new_report_event.soTerms = ['']
    new_report_event.soNames = ['']

    return validate_object(object_to_validate=new_report_event, object_type=object_type)


def get_valid_reported_somatic_variant_3_1_0():
    object_type = reports_3_1_0.ReportedSomaticVariants
    new_variant = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_variant.somaticOrGermline = reports_3_1_0.SomaticOrGermline.unknown
    new_variant.reportedVariantCancer.reportEvents[0] = get_valid_report_event_cancer_3_1_0()
    new_variant.reportedVariantCancer.position = 0
    new_variant.somaticOrGermline = reports_3_1_0.SomaticOrGermline.somatic

    return validate_object(object_to_validate=new_variant, object_type=object_type)


def get_valid_cancer_interpreted_genome_3_1_0():
    object_type = reports_3_1_0.CancerInterpretedGenome
    new_cig = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cig.softwareVersions = {'this': 'that'}
    new_cig.referenceDatabasesVersions = {'this': 'that'}
    new_cig.reportedStructuralVariants[0] = get_valid_reported_somatic_structural_variant_3_1_0()
    new_cig.reportedVariants[0] = get_valid_reported_somatic_variant_3_1_0()

    return validate_object(object_to_validate=new_cig, object_type=object_type)


def get_valid_cancer_sample_3_0_0():
    object_type = reports_3_0_0.CancerSample
    new_sample = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_sample.sampleType = reports_3_0_0.SampleType.germline

    return validate_object(object_to_validate=new_sample, object_type=object_type)


def get_valid_cancer_sample_3_1_0():
    object_type = reports_3_0_0.CancerSample
    new_sample = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_sample.sampleType = reports_3_0_0.SampleType.germline

    return validate_object(object_to_validate=new_sample, object_type=object_type)


def get_valid_clinical_report_cancer_2_1_0():
    object_type = reports_2_1_0.ClinicalReportCancer
    new_crc = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_crc.softwareVersions = {'this': 'that'}
    new_crc.referenceDatabasesVersions = {'this': 'that'}
    new_crc.candidateStructuralVariants[0] = get_valid_reported_structural_variant_2_1_0()
    new_crc.candidateVariants[0] = get_valid_reported_variant_2_1_0()
    new_crc.genePanelsCoverage = {"panel_name": [{"gene1": "gene1_coverage"}]}
    new_crc.cancerParticipant = get_valid_cancer_participant_2_1_0()

    return validate_object(object_to_validate=new_crc, object_type=object_type)


def get_valid_clinical_report_cancer_3_0_0():
    object_type = reports_3_0_0.ClinicalReportCancer
    new_crc = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_crc.softwareVersions = {'this': 'that'}
    new_crc.referenceDatabasesVersions = {'this': 'that'}
    new_crc.candidateStructuralVariants[0] = get_valid_reported_somatic_structural_variant_3_0_0()
    new_crc.candidateVariants[0] = get_valid_reported_somatic_variant_3_0_0()
    new_crc.genePanelsCoverage = {"panel_name": [{"gene1": "gene1_coverage"}]}
    new_crc.cancerParticipant = get_valid_cancer_participant_3_0_0()

    return validate_object(object_to_validate=new_crc, object_type=object_type)


def get_valid_clinical_report_cancer_3_1_0():
    object_type = reports_3_1_0.ClinicalReportCancer
    new_crc = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_crc.softwareVersions = {'this': 'that'}
    new_crc.referenceDatabasesVersions = {'this': 'that'}
    new_crc.candidateStructuralVariants[0] = get_valid_reported_somatic_structural_variant_3_1_0()
    new_crc.candidateVariants[0] = get_valid_reported_somatic_variant_3_1_0()
    new_crc.genePanelsCoverage = {"panel_name": [{"gene1": "gene1_coverage"}]}
    new_crc.cancerParticipant = get_valid_cancer_participant_3_1_0()

    return validate_object(object_to_validate=new_crc, object_type=object_type)


def get_valid_clinical_report_cancer_4_0_0():
    object_type = reports_4_0_0.ClinicalReportCancer
    new_crc = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_crc.softwareVersions = {'this': 'that'}
    new_crc.referenceDatabasesVersions = {'this': 'that'}
    new_crc.candidateStructuralVariants[0] = get_valid_reported_somatic_structural_variant_4_0_0()
    new_crc.candidateVariants[0] = get_valid_reported_somatic_variant_4_0_0()
    new_crc.genePanelsCoverage = {"panel_name": [{"gene1": "gene1_coverage"}]}
    new_crc.cancerParticipant = get_valid_cancer_participant_1_0_0()

    return validate_object(object_to_validate=new_crc, object_type=object_type)


def get_valid_called_genotype_2_1_0():
    object_type = reports_2_1_0.CalledGenotype
    new_cg = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cg.genotype = ''

    return validate_object(object_to_validate=new_cg, object_type=object_type)


def get_valid_report_event_2_1_0():
    object_type = reports_2_1_0.ReportEvent
    new_report_event = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_report_event.modeOfInheritance = reports_2_1_0.ReportedModeOfInheritance.unknown
    new_report_event.score = 0.0
    new_report_event.genomicFeature.featureType = reports_2_1_0.FeatureTypes.RegulatoryRegion
    new_report_event.genomicFeature.ids = {}
    new_report_event.penetrance = reports_2_1_0.Penetrance.complete

    return validate_object(object_to_validate=new_report_event, object_type=object_type)


def get_valid_reported_variant_2_1_0():
    object_type = reports_2_1_0.ReportedVariant
    new_rv = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_rv.calledGenotypes[0] = get_valid_called_genotype_2_1_0()
    new_rv.reportEvents[0] = get_valid_report_event_2_1_0()
    new_rv.position = 0
    new_rv.evidenceIds = {}
    new_rv.comments = ['']
    new_rv.dbSNPid = ''
    new_rv.additionalNumericVariantAnnotations = {}
    new_rv.additionalTextualVariantAnnotations = {}

    return validate_object(object_to_validate=new_rv, object_type=object_type)


def get_valid_reported_structural_variant_2_1_0():
    object_type = reports_2_1_0.ReportedStructuralVariant
    new_rsv = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_rsv.calledGenotypes[0] = get_valid_called_genotype_2_1_0()
    new_rsv.reportEvents[0] = get_valid_report_event_2_1_0()
    new_rsv.start, new_rsv.end = 1, 2

    return validate_object(object_to_validate=new_rsv, object_type=object_type)


def get_valid_interpreted_genome_rd_2_1_0():
    object_type = reports_2_1_0.InterpretedGenomeRD
    new_ig_rd = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_ig_rd.softwareVersions = {}
    new_ig_rd.referenceDatabasesVersions = {}
    new_ig_rd.penetrance = reports_2_1_0.Penetrance.complete
    new_ig_rd.modeOfInheritance = reports_2_1_0.ReportedModeOfInheritance.unknown
    new_ig_rd.reportedVariants[0] = get_valid_reported_variant_2_1_0()
    new_ig_rd.reportedStructuralVariants[0] = get_valid_reported_structural_variant_2_1_0()

    return validate_object(object_to_validate=new_ig_rd, object_type=object_type)


def get_valid_disease_penetrance_4_0_0():
    object_type = reports_4_0_0.DiseasePenetrance
    dp = MockModelObject(object_type=object_type).get_valid_empty_object()
    dp.penetrance = reports_4_0_0.Penetrance.incomplete

    return validate_object(object_to_validate=dp, object_type=object_type)

def get_valid_disease_penetrance_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.DiseasePenetrance
    dp = MockModelObject(object_type=object_type).get_valid_empty_object()
    dp.penetrance = reports_4_2_0_SNAPSHOT.Penetrance.incomplete

    return validate_object(object_to_validate=dp, object_type=object_type)


def get_valid_disease_penetrance_3_1_0():
    object_type = reports_3_1_0.DiseasePenetrance
    dp = MockModelObject(object_type=object_type).get_valid_empty_object()
    dp.penetrance = reports_3_1_0.Penetrance.incomplete

    return validate_object(object_to_validate=dp, object_type=object_type)


def get_valid_disease_penetrance_3_0_0():
    object_type = reports_3_0_0.DiseasePenetrance
    dp = MockModelObject(object_type=object_type).get_valid_empty_object()
    dp.penetrance = reports_3_0_0.Penetrance.incomplete

    return validate_object(object_to_validate=dp, object_type=object_type)


def get_valid_sample_4_0_0():
    object_type = reports_4_0_0.Sample
    sample = MockModelObject(object_type=object_type).get_valid_empty_object()
    sample.labSampleId = 1

    return validate_object(object_to_validate=sample, object_type=object_type)


def get_valid_sample_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.Sample
    sample = MockModelObject(object_type=object_type).get_valid_empty_object()
    sample.labSampleId = 1

    return validate_object(object_to_validate=sample, object_type=object_type)


def get_valid_inbreeding_coefficient_4_0_0():
    object_type = reports_4_0_0.InbreedingCoefficient
    ic = MockModelObject(object_type=object_type).get_valid_empty_object()
    ic.coefficient = 0.0

    return validate_object(object_to_validate=ic, object_type=object_type)


def get_valid_inbreeding_coefficient_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.InbreedingCoefficient
    ic = MockModelObject(object_type=object_type).get_valid_empty_object()
    ic.coefficient = 0.0

    return validate_object(object_to_validate=ic, object_type=object_type)


def get_valid_inbreeding_coefficient_3_1_0():
    object_type = reports_3_1_0.InbreedingCoefficient
    ic = MockModelObject(object_type=object_type).get_valid_empty_object()
    ic.coefficient = 0.0

    return validate_object(object_to_validate=ic, object_type=object_type)

def get_valid_inbreeding_coefficient_3_0_0():
    object_type = reports_3_0_0.InbreedingCoefficient
    ic = MockModelObject(object_type=object_type).get_valid_empty_object()
    ic.coefficient = 0.0

    return validate_object(object_to_validate=ic, object_type=object_type)


def get_valid_inbreeding_coefficient_2_1_0():
    object_type = reports_2_1_0.InbreedingCoefficient
    ic = MockModelObject(object_type=object_type).get_valid_empty_object()
    ic.coefficient = 0.0

    return validate_object(object_to_validate=ic, object_type=object_type)


def get_valid_chi_square_1k_genomes_phase_3_pop_4_0_0():
    object_type = reports_4_0_0.ChiSquare1KGenomesPhase3Pop
    cs = MockModelObject(object_type=object_type).get_valid_empty_object()
    cs.chiSquare = 0.0
    cs.kGSuperPopCategory = reports_4_0_0.KGSuperPopCategory.AFR

    return validate_object(object_to_validate=cs, object_type=object_type)


def get_valid_chi_square_1k_genomes_phase_3_pop_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.ChiSquare1KGenomesPhase3Pop
    cs = MockModelObject(object_type=object_type).get_valid_empty_object()
    cs.chiSquare = 0.0
    cs.kgSuperPopCategory = reports_4_2_0_SNAPSHOT.KgSuperPopCategory.AFR

    return validate_object(object_to_validate=cs, object_type=object_type)


def get_valid_chi_square_1k_genomes_phase_3_pop_3_1_0():
    object_type = reports_3_1_0.ChiSquare1KGenomesPhase3Pop
    cs = MockModelObject(object_type=object_type).get_valid_empty_object()
    cs.chiSquare = 0.0
    cs.kgSuperPopCategory = reports_3_1_0.KGSuperPopCategory.AFR

    return validate_object(object_to_validate=cs, object_type=object_type)


def get_valid_chi_square_1k_genomes_phase_3_pop_3_0_0():
    object_type = reports_3_0_0.ChiSquare1KGenomesPhase3Pop
    cs = MockModelObject(object_type=object_type).get_valid_empty_object()
    cs.chiSquare = 0.0
    cs.kGSuperPopCategory = reports_3_0_0.KGSuperPopCategory.AFR

    return validate_object(object_to_validate=cs, object_type=object_type)


def get_valid_chi_square_1k_genomes_phase_3_pop_2_1_0():
    object_type = reports_2_1_0.ChiSquare1KGenomesPhase3Pop
    cs = MockModelObject(object_type=object_type).get_valid_empty_object()
    cs.chiSquare = 0.0
    cs.kGSuperPopCategory = reports_2_1_0.KGSuperPopCategory.AFR

    return validate_object(object_to_validate=cs, object_type=object_type)


def get_valid_ancestries_4_0_0():
    object_type = reports_4_0_0.Ancestries
    ancestries = MockModelObject(object_type=object_type).get_valid_empty_object()
    ancestries.chiSquare1KGenomesPhase3Pop[0] = get_valid_chi_square_1k_genomes_phase_3_pop_4_0_0()

    return validate_object(object_to_validate=ancestries, object_type=object_type)


def get_valid_ancestries_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.Ancestries
    ancestries = MockModelObject(object_type=object_type).get_valid_empty_object()
    ancestries.chiSquare1KGenomesPhase3Pop[0] = get_valid_chi_square_1k_genomes_phase_3_pop_4_2_0_SNAPSHOT()

    return validate_object(object_to_validate=ancestries, object_type=object_type)


def get_valid_ancestries_3_1_0():
    object_type = reports_3_1_0.Ancestries
    ancestries = MockModelObject(object_type=object_type).get_valid_empty_object()
    ancestries.chiSquare1KGenomesPhase3Pop[0] = get_valid_chi_square_1k_genomes_phase_3_pop_3_1_0()

    return validate_object(object_to_validate=ancestries, object_type=object_type)


def get_valid_ancestries_3_0_0():
    object_type = reports_3_0_0.Ancestries
    ancestries = MockModelObject(object_type=object_type).get_valid_empty_object()
    ancestries.chiSquare1KGenomesPhase3Pop[0] = get_valid_chi_square_1k_genomes_phase_3_pop_3_0_0()

    return validate_object(object_to_validate=ancestries, object_type=object_type)


def get_valid_ancestries_2_1_0():
    object_type = reports_2_1_0.Ancestries
    ancestries = MockModelObject(object_type=object_type).get_valid_empty_object()
    ancestries.chiSquare1KGenomesPhase3Pop[0] = get_valid_chi_square_1k_genomes_phase_3_pop_2_1_0()

    return validate_object(object_to_validate=ancestries, object_type=object_type)


def get_valid_pedigree_members_4_0_0():
    object_type = reports_4_0_0.PedigreeMember
    member = MockModelObject(object_type=object_type).get_valid_empty_object()
    member.sex = reports_4_0_0.Sex.UNKNOWN
    member.samples[0] = get_valid_sample_4_0_0()
    member.inbreedingCoefficient = get_valid_inbreeding_coefficient_4_0_0()
    member.ancestries = get_valid_ancestries_4_0_0()

    return validate_object(object_to_validate=member, object_type=object_type)


def get_valid_pedigree_members_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.PedigreeMember
    member = MockModelObject(object_type=object_type).get_valid_empty_object()
    member.sex = reports_4_2_0_SNAPSHOT.Sex.UNKNOWN
    member.samples[0] = get_valid_sample_4_2_0_SNAPSHOT()
    member.inbreedingCoefficient = get_valid_inbreeding_coefficient_4_2_0_SNAPSHOT()
    member.ancestries = get_valid_ancestries_4_2_0_SNAPSHOT()

    return validate_object(object_to_validate=member, object_type=object_type)


def get_valid_pedigree_participant_rd_3_1_0():
    object_type = reports_3_1_0.RDParticipant
    participant = MockModelObject(object_type=object_type).get_valid_empty_object()

    participant.pedigreeId = 1
    participant.isProband = False
    participant.sex = reports_3_1_0.Sex.undetermined
    participant.ancestries = get_valid_ancestries_3_1_0()
    participant.lifeStatus = reports_3_1_0.LifeStatus.alive
    participant.adoptedStatus = reports_3_1_0.AdoptedStatus.not_adopted
    participant.affectionStatus = reports_3_1_0.AffectionStatus.unknown
    participant.consanguineousParents = reports_3_1_0.TernaryOption.unknown
    participant.inbreedingCoefficient = get_valid_inbreeding_coefficient_3_1_0()

    return validate_object(object_to_validate=participant, object_type=object_type)


def get_valid_pedigree_participant_rd_3_0_0():
    object_type = reports_3_0_0.RDParticipant
    participant = MockModelObject(object_type=object_type).get_valid_empty_object()

    participant.pedigreeId = 1
    participant.isProband = False
    participant.sex = reports_3_0_0.Sex.undetermined
    participant.ancestries = get_valid_ancestries_3_0_0()
    participant.lifeStatus = reports_3_0_0.LifeStatus.alive
    participant.adoptedStatus = reports_3_0_0.AdoptedStatus.not_adopted
    participant.affectionStatus = reports_3_0_0.AffectionStatus.unknown
    participant.consanguineousParents = reports_3_0_0.TernaryOption.unknown
    participant.inbreedingCoefficient = get_valid_inbreeding_coefficient_3_0_0()

    return validate_object(object_to_validate=participant, object_type=object_type)


def get_valid_pedigree_participant_rd_2_1_0():
    object_type = reports_2_1_0.RDParticipant
    participant = MockModelObject(object_type=object_type).get_valid_empty_object()

    participant.pedigreeId = 1
    participant.isProband = False
    participant.sex = "male"
    participant.ancestries = get_valid_ancestries_2_1_0()
    participant.lifeStatus = reports_2_1_0.LifeStatus.alive
    participant.adoptedStatus = reports_2_1_0.AdoptedStatus.not_adopted
    participant.affectionStatus = reports_2_1_0.AffectionStatus.unknown
    participant.consanguineousParents = reports_2_1_0.TernaryOption.unknown
    participant.inbreedingCoefficient = get_valid_inbreeding_coefficient_2_1_0()

    return validate_object(object_to_validate=participant, object_type=object_type)


def get_valid_pedigree_4_0_0():
    object_type = reports_4_0_0.Pedigree
    pedigree = MockModelObject(object_type=object_type).get_valid_empty_object()
    pedigree.diseasePenetrances[0] = get_valid_disease_penetrance_4_0_0()
    pedigree.readyForAnalysis = True
    pedigree.members[0] = get_valid_pedigree_members_4_0_0()

    return validate_object(object_to_validate=pedigree, object_type=object_type)


def get_valid_pedigree_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.Pedigree
    pedigree = MockModelObject(object_type=object_type).get_valid_empty_object()
    pedigree.diseasePenetrances[0] = get_valid_disease_penetrance_4_2_0_SNAPSHOT()
    pedigree.readyForAnalysis = True
    pedigree.members[0] = get_valid_pedigree_members_4_2_0_SNAPSHOT()

    return validate_object(object_to_validate=pedigree, object_type=object_type)


def get_valid_pedigree_3_1_0():
    object_type = reports_3_1_0.Pedigree
    pedigree = MockModelObject(object_type=object_type).get_valid_empty_object()
    pedigree.diseasePenetrances[0] = get_valid_disease_penetrance_3_1_0()
    pedigree.readyForAnalysis = True
    pedigree.participants[0] = get_valid_pedigree_participant_rd_3_1_0()

    return validate_object(object_to_validate=pedigree, object_type=object_type)


def get_valid_pedigree_3_0_0():
    object_type = reports_3_0_0.Pedigree
    pedigree = MockModelObject(object_type=object_type).get_valid_empty_object()
    pedigree.diseasePenetrances[0] = get_valid_disease_penetrance_3_0_0()
    pedigree.readyForAnalysis = True
    pedigree.participants[0] = get_valid_pedigree_participant_rd_3_0_0()

    return validate_object(object_to_validate=pedigree, object_type=object_type)


def get_valid_pedigree_2_1_0():
    object_type = reports_2_1_0.Pedigree
    pedigree = MockModelObject(object_type=object_type).get_valid_empty_object()
    pedigree.participants[0] = get_valid_pedigree_participant_rd_2_1_0()

    return validate_object(object_to_validate=pedigree, object_type=object_type)


def get_valid_interpretation_request_rd_4_0_0():
    object_type = reports_4_0_0.InterpretationRequestRD
    new_ir_rd = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_ir_rd.workspace = ['']
    new_ir_rd.annotationFile.fileType = reports_4_0_0.FileType.ANN
    new_ir_rd.bams = [new_ir_rd.bams]
    new_ir_rd.bams[0].fileType = reports_4_0_0.FileType.BAM
    new_ir_rd.bigWigs = [new_ir_rd.bigWigs]
    new_ir_rd.bigWigs[0].fileType = reports_4_0_0.FileType.BigWig
    new_ir_rd.vcfs = [new_ir_rd.vcfs]
    new_ir_rd.vcfs[0].fileType = reports_4_0_0.FileType.VCF_CNV
    new_ir_rd.interpretationRequestVersion = 1
    new_ir_rd.pedigreeDiagram.fileType = reports_4_0_0.FileType.OTHER
    new_ir_rd.tieredVariants[0] = get_valid_reported_variant_4_0_0()
    new_ir_rd.pedigree = get_valid_pedigree_4_0_0()

    return validate_object(object_to_validate=new_ir_rd, object_type=object_type)


def get_valid_interpretation_request_rd_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.InterpretationRequestRD
    new_ir_rd = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_ir_rd.workspace = ['']
    new_ir_rd.annotationFile.fileType = reports_4_2_0_SNAPSHOT.FileType.ANN
    new_ir_rd.bams = [new_ir_rd.bams]
    new_ir_rd.bams[0].fileType = reports_4_2_0_SNAPSHOT.FileType.BAM
    new_ir_rd.bigWigs = [new_ir_rd.bigWigs]
    new_ir_rd.bigWigs[0].fileType = reports_4_2_0_SNAPSHOT.FileType.BigWig
    new_ir_rd.vcfs = [new_ir_rd.vcfs]
    new_ir_rd.vcfs[0].fileType = reports_4_2_0_SNAPSHOT.FileType.VCF_CNV
    new_ir_rd.interpretationRequestVersion = 1
    new_ir_rd.pedigreeDiagram.fileType = reports_4_2_0_SNAPSHOT.FileType.OTHER
    new_ir_rd.tieredVariants[0] = get_valid_reported_variant_4_2_0_SNAPSHOT()
    new_ir_rd.pedigree = get_valid_pedigree_4_2_0_SNAPSHOT()

    return validate_object(object_to_validate=new_ir_rd, object_type=object_type)


def get_valid_interpretation_request_rd_3_1_0():
    object_type = reports_3_1_0.InterpretationRequestRD
    new_ir_rd = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_ir_rd.workspace = ['']
    new_ir_rd.vcfs = [new_ir_rd.vcfs]
    new_ir_rd.vcfs[0].fileType = reports_3_1_0.FileType.VCF_CNV
    new_ir_rd.bams = [new_ir_rd.bams]
    new_ir_rd.bams[0].fileType = reports_3_1_0.FileType.BAM
    new_ir_rd.bigWigs = [new_ir_rd.bigWigs]
    new_ir_rd.bigWigs[0].fileType = reports_3_1_0.FileType.BigWig
    new_ir_rd.interpretationRequestVersion = 1
    new_ir_rd.tieredVariants[0] = get_valid_reported_variant_3_1_0()
    new_ir_rd.annotationFile.fileType = reports_3_1_0.FileType.ANN
    new_ir_rd.pedigreeDiagram.fileType = reports_3_1_0.FileType.OTHER
    new_ir_rd.pedigree = get_valid_pedigree_3_1_0()

    return validate_object(object_to_validate=new_ir_rd, object_type=object_type)


def get_valid_virtual_panel_2_1_0():
    object_type = reports_2_1_0.VirtualPanel
    vp = MockModelObject(object_type=object_type).get_valid_empty_object()
    vp.geneIds = [""]
    vp.relevantRegions.fileType = reports_2_1_0.FileType.ANN
    vp.clinicalRelevantVariants.fileType = reports_2_1_0.FileType.ANN

    return validate_object(object_to_validate=vp, object_type=object_type)


def get_valid_interpretation_request_rd_2_1_0():
    object_type = reports_2_1_0.InterpretationRequestRD
    new_ir_rd = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_ir_rd.workspace = ['']
    new_ir_rd.VCFs = [new_ir_rd.VCFs]
    new_ir_rd.VCFs[0].fileType = reports_2_1_0.FileType.VCF_CNV
    new_ir_rd.BAMs = [new_ir_rd.BAMs]
    new_ir_rd.BAMs[0].fileType = reports_2_1_0.FileType.BAM
    new_ir_rd.bigWigs = [new_ir_rd.bigWigs]
    new_ir_rd.bigWigs[0].fileType = reports_2_1_0.FileType.BigWig
    new_ir_rd.InterpretationRequestVersion = 1
    new_ir_rd.annotationFile.fileType = reports_2_1_0.FileType.ANN
    new_ir_rd.modeOfInheritance = reports_2_1_0.ModeOfInheritance.unknown
    new_ir_rd.pedigreeDiagram.fileType = reports_2_1_0.FileType.ANN
    new_ir_rd.pedigree = get_valid_pedigree_2_1_0()
    new_ir_rd.TieredVariants[0] = get_valid_reported_variant_2_1_0()
    # new_ir_rd.virtualPanel = get_valid_virtual_panel_2_1_0()
    new_ir_rd.virtualPanel = None

    return validate_object(object_to_validate=new_ir_rd, object_type=object_type)


def get_valid_cancer_interpreted_genome_4_0_0():
    object_type = reports_4_0_0.CancerInterpretedGenome
    new_cig = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cig.softwareVersions = {'this': 'that'}
    new_cig.referenceDatabasesVersions = {'this': 'that'}
    new_cig.reportedStructuralVariants[0] = get_valid_reported_somatic_structural_variant_4_0_0()
    new_cig.reportedVariants[0] = get_valid_reported_somatic_variant_4_0_0()

    return validate_object(object_to_validate=new_cig, object_type=object_type)


def get_valid_reported_somatic_structural_variant_2_1_0():
    object_type = reports_2_1_0.ReportedSomaticStructuralVariants
    rssv = MockModelObject(object_type=object_type).get_valid_empty_object()
    rssv.somaticOrGermline = reports_2_1_0.SomaticOrGermline.unknown
    rssv.reportedStructuralVariant = rssv.reportedStructuralVariant[0]
    rssv.reportedStructuralVariant.start = 1
    rssv.reportedStructuralVariant.end = 2
    rssv.reportedStructuralVariant.reportEvents[0] = get_valid_report_event_2_1_0()

    return validate_object(object_to_validate=rssv, object_type=object_type)


def get_valid_report_event_cancer_2_1_0():
    object_type = reports_2_1_0.ReportEventCancer
    new_report_event = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_report_event.actions[0].variantActionable = False
    new_report_event.actions[0].actionType = reports_2_1_0.ActionType.Diagnosis
    new_report_event.genomicFeatureCancer.featureType = reports_2_1_0.FeatureTypes.Gene
    new_report_event.tier = reports_2_1_0.Tier.NONE
    new_report_event.soTerms = ['']
    new_report_event.soNames = ['']

    return validate_object(object_to_validate=new_report_event, object_type=object_type)


def get_valid_reported_somatic_variant_2_1_0():
    object_type = reports_2_1_0.ReportedSomaticVariants
    rsv = MockModelObject(object_type=object_type).get_valid_empty_object()
    rsv.somaticOrGermline = reports_2_1_0.SomaticOrGermline.unknown

    rsv.reportedVariant = get_valid_reported_variant_2_1_0()

    rsv.reportedVariant.reportEvents[0] = get_valid_report_event_2_1_0()
    rsv.reportedVariant.position = 0
    # rsv.somaticOrGermline = reports_2_1_0.SomaticOrGermline.somatic

    return validate_object(object_to_validate=rsv, object_type=object_type)


def get_valid_cancer_interpreted_genome_2_1_0():
    object_type = reports_2_1_0.CancerInterpretedGenome
    new_cig = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cig.softwareVersions = {'this': 'that'}
    new_cig.referenceDatabasesVersions = {'this': 'that'}
    new_cig.reportedStructuralVariants[0] = get_valid_reported_somatic_structural_variant_2_1_0()
    new_cig.reportedVariants[0] = get_valid_reported_somatic_variant_2_1_0()

    return validate_object(object_to_validate=new_cig, object_type=object_type)


def get_valid_cancer_interpretation_request_4_0_0():
    object_type = reports_4_0_0.CancerInterpretationRequest
    new_cir = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cir.workspace = ['']
    new_cir.bams = [new_cir.bams]
    new_cir.bams[0].fileType = reports_4_0_0.FileType.BAM
    new_cir.bigWigs = [new_cir.bigWigs]
    new_cir.bigWigs[0].fileType = reports_4_0_0.FileType.BigWig
    new_cir.vcfs = [new_cir.vcfs]
    new_cir.vcfs[0].fileType = reports_4_0_0.FileType.VCF_small

    new_cir.cancerParticipant = get_valid_cancer_participant_1_0_0()
    new_cir.annotationFile.fileType = reports_4_0_0.FileType.ANN
    new_cir.structuralTieredVariants[0] = get_valid_reported_somatic_structural_variant_4_0_0()
    new_cir.tieredVariants[0] = get_valid_reported_somatic_variant_4_0_0()
    new_cir.reportVersion = 1

    return validate_object(object_to_validate=new_cir, object_type=object_type)


def get_valid_cancer_interpretation_request_4_2_0_SNAPSHOT():
    object_type = reports_4_2_0_SNAPSHOT.CancerInterpretationRequest
    new_cir = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cir.workspace = ['']
    new_cir.bams = [new_cir.bams]
    new_cir.bams[0].fileType = reports_4_2_0_SNAPSHOT.FileType.BAM
    new_cir.bigWigs = [new_cir.bigWigs]
    new_cir.bigWigs[0].fileType = reports_4_2_0_SNAPSHOT.FileType.BigWig
    new_cir.vcfs = [new_cir.vcfs]
    new_cir.vcfs[0].fileType = reports_4_2_0_SNAPSHOT.FileType.VCF_small
    new_cir.cancerParticipant = get_valid_cancer_participant_1_0_4_SNAPSHOT()

    new_cir.annotationFile.fileType = reports_4_2_0_SNAPSHOT.FileType.ANN
    new_cir.structuralTieredVariants[0] = get_valid_reported_somatic_structural_variant_4_2_0_SNAPSHOT()
    new_cir.tieredVariants[0] = get_valid_reported_somatic_variant_4_2_0_SNAPSHOT()
    new_cir.reportVersion = 1

    return validate_object(object_to_validate=new_cir, object_type=object_type)


def get_valid_cancer_interpretation_request_3_1_0():
    object_type = reports_3_1_0.CancerInterpretationRequest
    new_cir = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cir.workspace = ['']
    new_cir.bams = [new_cir.bams]
    new_cir.bams[0].fileType = reports_3_1_0.FileType.BAM
    new_cir.bigWigs = [new_cir.bigWigs]
    new_cir.bigWigs[0].fileType = reports_3_1_0.FileType.BigWig
    new_cir.vcfs = [new_cir.vcfs]
    new_cir.vcfs[0].fileType = reports_3_1_0.FileType.VCF_small
    new_cir.cancerParticipant.cancerSamples[0].sampleType = reports_3_1_0.SampleType.tumor
    new_cir.annotationFile.fileType = reports_3_1_0.FileType.ANN
    new_cir.structuralTieredVariants[0] = get_valid_reported_somatic_structural_variant_3_1_0()
    new_cir.tieredVariants[0] = get_valid_reported_somatic_variant_3_1_0()
    new_cir.reportVersion = 1

    return validate_object(object_to_validate=new_cir, object_type=object_type)


def get_valid_cancer_interpretation_request_2_1_0():
    object_type = reports_2_1_0.CancerInterpretationRequest
    new_cir = MockModelObject(object_type=object_type).get_valid_empty_object()
    new_cir.workspace = ['']
    new_cir.BAMs = [new_cir.BAMs]
    new_cir.BAMs[0].fileType = reports_2_1_0.FileType.BAM
    new_cir.bigWigs = [new_cir.bigWigs]
    new_cir.bigWigs[0].fileType = reports_2_1_0.FileType.BigWig
    new_cir.VCFs = [new_cir.VCFs]
    new_cir.VCFs[0].fileType = reports_2_1_0.FileType.VCF_small
    new_cir.cancerParticipant.cancerSamples[0].sampleType = reports_2_1_0.SampleType.tumor
    new_cir.annotationFile.fileType = reports_3_1_0.FileType.ANN
    new_cir.reportVersion = 1

    return validate_object(object_to_validate=new_cir, object_type=object_type)


def get_valid_tiered_variant_inject_rd_0_3_1():
    object_type = cva_0_3_1.TieredVariantInjectRD
    new_tvi_rd = MockModelObject(object_type=object_type).get_valid_empty_object()

    new_tvi_rd.reportModelVersion = 'foo'
    new_tvi_rd.id = 'foo'
    new_tvi_rd.version = 1
    new_tvi_rd.familyId = 'foo'
    new_tvi_rd.cohortId = 'foo'
    new_tvi_rd.author = 'foo'
    new_tvi_rd.authorVersion = 'foo'
    new_tvi_rd.workspace = ['foo']
    new_tvi_rd.interpretationRequest = get_valid_interpretation_request_rd_3_1_0()

    return validate_object(object_to_validate=new_tvi_rd, object_type=object_type)


def get_valid_tiered_variant_inject_rd_0_4_0():
    object_type = cva_0_4_0_SNAPSHOT.TieredVariantInjectRD
    new_tvi_rd = cva_0_4_0_SNAPSHOT.TieredVariantInjectRD()

    new_tvi_rd.assembly = cva_0_4_0_SNAPSHOT.SupportedAssembly.GRCh37
    new_tvi_rd.reportModelVersion = 'foo'
    new_tvi_rd.id = 'foo'
    new_tvi_rd.version = 1
    new_tvi_rd.groupId = 'foo'
    new_tvi_rd.cohortId = 'foo'
    new_tvi_rd.author = 'foo'
    new_tvi_rd.authorVersion = 'foo'
    new_tvi_rd.workspace = ['foo']
    new_tvi_rd.interpretationRequest = get_valid_interpretation_request_rd_4_2_0_SNAPSHOT()

    return validate_object(object_to_validate=new_tvi_rd, object_type=object_type)


def get_valid_tiered_variant_inject_cancer_0_4_0():
    object_type = cva_0_4_0_SNAPSHOT.TieredVariantInjectCancer
    new_tvi_rd = cva_0_4_0_SNAPSHOT.TieredVariantInjectCancer()

    new_tvi_rd.assembly = cva_0_4_0_SNAPSHOT.SupportedAssembly.GRCh37
    new_tvi_rd.reportModelVersion = 'foo'
    new_tvi_rd.id = 'foo'
    new_tvi_rd.version = 1
    new_tvi_rd.groupId = 'foo'
    new_tvi_rd.cohortId = 'foo'
    new_tvi_rd.author = 'foo'
    new_tvi_rd.authorVersion = 'foo'
    new_tvi_rd.workspace = ['foo']
    new_tvi_rd.interpretationRequest = get_valid_cancer_interpretation_request_4_2_0_SNAPSHOT()

    return validate_object(object_to_validate=new_tvi_rd, object_type=object_type)


def get_valid_reported_variant_inject_rd_0_3_1():
    object_type = cva_0_3_1.ReportedVariantInjectRD
    new_tvi_rd = cva_0_3_1.ReportedVariantInjectRD(
        reportModelVersion='foo',
        parentId='foo',
        parentVersion=1,
        id='foo',
        version=1,
        familyId='foo',
        cohortId='foo',
        author='foo',
        authorVersion='foo',
        workspace=['foo'],
        interpretedGenome=get_valid_interpreted_genome_rd_3_1_0()
    )

    return validate_object(object_to_validate=new_tvi_rd, object_type=object_type)


def get_valid_reported_variant_inject_rd_0_4_0():
    object_type = cva_0_4_0_SNAPSHOT.ReportedVariantInjectRD
    new_tvi_rd = cva_0_4_0_SNAPSHOT.ReportedVariantInjectRD(
        assembly=cva_0_4_0_SNAPSHOT.SupportedAssembly.GRCh37,
        reportModelVersion='foo',
        id='foo',
        parentId='foo',
        parentVersion=1,
        version=1,
        groupId='foo',
        cohortId='foo',
        author='foo',
        authorVersion='foo',
        workspace=['foo'],
        interpretedGenome=get_valid_interpreted_genome_rd_4_2_0_SNAPSHOT()
    )

    return validate_object(object_to_validate=new_tvi_rd, object_type=object_type)


def get_valid_candidate_variant_inject_rd_0_3_1():
    object_type = cva_0_3_1.CandidateVariantInjectRD
    new_tvi_rd = cva_0_3_1.CandidateVariantInjectRD(
        author='foo',
        parentId='foo',
        reportModelVersion='foo',
        authorVersion='foo',
        version=1,
        workspace=['foo'],
        familyId='foo',
        cohortId='foo',
        parentVersion=1,
        id='foo',
        clinicalReport=get_valid_clinical_report_rd_3_1_0()
    )

    return validate_object(object_to_validate=new_tvi_rd, object_type=object_type)


def get_valid_candidate_variant_inject_rd_0_4_0():
    object_type = cva_0_4_0_SNAPSHOT.CandidateVariantInjectRD
    new_tvi_rd = cva_0_4_0_SNAPSHOT.CandidateVariantInjectRD(
        assembly=cva_0_4_0_SNAPSHOT.SupportedAssembly.GRCh37,
        reportModelVersion='foo',
        id='foo',
        parentId='foo',
        parentVersion=1,
        version=1,
        groupId='foo',
        cohortId='foo',
        author='foo',
        authorVersion='foo',
        workspace=['foo'],
        clinicalReport=get_valid_clinical_report_rd_4_2_0_SNAPSHOT()
    )

    return validate_object(object_to_validate=new_tvi_rd, object_type=object_type)

from protocols import participant_1_0_0
from protocols import reports_3_0_0
from protocols.util import handle_avro_errors
from protocols.migration.base_migration import BaseMigration


class MigrateReports3ToParticipant1(BaseMigration):
    """
    Any participant with empty labId in tumour or germline sample will fail to validate.
    """
    old_model = reports_3_0_0
    new_model = participant_1_0_0

    def migrate_cancer_participant(self, old_cancer_participant):
        """
        :type old_cancer_participant: reports_3_0_0.CancerParticipant
        :rtype: participant_1_0_0.CancerParticipant
        """
        new_cancer_participant = self.new_model.CancerParticipant.fromJsonDict(old_cancer_participant.toJsonDict())

        new_cancer_participant.versionControl.GitVersionControl = '1.0.0'
        new_cancer_participant.additionalInformation = old_cancer_participant.cancerDemographics.additionalInformation
        new_cancer_participant.assignedICD10 = old_cancer_participant.cancerDemographics.assignedICD10
        new_cancer_participant.center = old_cancer_participant.cancerDemographics.center
        new_cancer_participant.LDPCode = old_cancer_participant.cancerDemographics.center
        new_cancer_participant.consentStatus = old_cancer_participant.cancerDemographics.consentStatus
        new_cancer_participant.sex = self.migrate_sex(old_sex=old_cancer_participant.cancerDemographics.sex)
        new_cancer_participant.individualId = old_cancer_participant.cancerDemographics.gelId
        new_cancer_participant.primaryDiagnosisDisease = old_cancer_participant.cancerDemographics.primaryDiagnosis
        new_cancer_participant.readyForAnalysis = True

        germline_samples = [
            sample for sample in old_cancer_participant.cancerSamples if sample.sampleType == self.old_model.SampleType.germline
        ]
        new_cancer_participant.germlineSamples = [self.migrate_germline_sample(sample) for sample in germline_samples]

        tumor_samples = [
            sample for sample in old_cancer_participant.cancerSamples if sample.sampleType == self.old_model.SampleType.tumor
        ]

        new_cancer_participant.tumourSamples = [self.migrate_tumor_sample(sample) for sample in tumor_samples]
        new_cancer_participant.matchedSamples = [self.migrate_match_samples(matched_sample) for matched_sample in
                                                 old_cancer_participant.matchedSamples]

        return self.validate_object(
            object_to_validate=new_cancer_participant, object_type=self.new_model.CancerParticipant
        )

    def migrate_tumor_sample(self, old_cancer_sample):

        new_tumour_sample = self.new_model.TumourSample.fromJsonDict(old_cancer_sample.toJsonDict())

        new_tumour_sample.TNMStageGrouping = old_cancer_sample.tmn_stage_grouping
        new_tumour_sample.TNMStageVersion = old_cancer_sample.tmn_stage_grouping
        new_tumour_sample.labSampleId = self.convert_string_to_integer(string=old_cancer_sample.labId)
        new_tumour_sample.programmePhase = old_cancer_sample.gelPhase

        new_tumour_sample.preparationMethod = old_cancer_sample.preservationMethod
        new_tumour_sample.source = participant_1_0_0.SampleSource.TUMOUR

        new_tumour_type = None
        if isinstance(old_cancer_sample.tumorType, basestring):
            old_tumour_type = old_cancer_sample.tumorType.upper()
            new_tumour_type = getattr(participant_1_0_0.TumourType, old_tumour_type, None)
        new_tumour_sample.tumourType = new_tumour_type

        new_tumour_content = None
        if isinstance(old_cancer_sample.tumorContent, basestring):
            old_tumor_content = old_cancer_sample.tumorContent
            new_tumour_content = getattr(participant_1_0_0.TumourContent, old_tumor_content.title(), None)
        new_tumour_sample.tumourContent = new_tumour_content

        new_tumour_sample.tumourSubType = old_cancer_sample.tumorSubType

        new_tumour_sample.tumourId = 1

        return self.validate_object(
            object_to_validate=new_tumour_sample, object_type=self.new_model.TumourSample
        )

    def migrate_match_samples(self, old_match_samples):
        new_match_sample = self.new_model.MatchedSamples.fromJsonDict(old_match_samples.toJsonDict())
        new_match_sample.tumourSampleId = old_match_samples.tumorSampleId
        return new_match_sample

    def migrate_germline_sample(self, old_cancer_sample):

        new_germline_sample = self.new_model.GermlineSample.fromJsonDict(old_cancer_sample.toJsonDict())

        new_germline_sample.labSampleId = self.convert_string_to_integer(string=old_cancer_sample.labId)
        new_germline_sample.source = old_cancer_sample.preservationMethod

        preservation_to_preparation_map = {
            reports_3_0_0.PreservationMethod.BLOOD: participant_1_0_0.PreparationMethod.EDTA,
            reports_3_0_0.PreservationMethod.SALIVA: participant_1_0_0.PreparationMethod.ORAGENE
        }
        new_germline_sample.preparationMethod = preservation_to_preparation_map.get(new_germline_sample.source)

        new_germline_sample.programmePhase = old_cancer_sample.gelPhase

        if new_germline_sample.validate(new_germline_sample.toJsonDict()):
            return new_germline_sample
        else:
            # TODO(Greg): Improve these error messages
            raise Exception('This model can not be converted: ', new_germline_sample.validate_parts())

    def migrate_sex(self, old_sex):
        sex_map = {
            'F': self.new_model.Sex.FEMALE,
            'M': self.new_model.Sex.MALE
        }
        return sex_map.get(old_sex, self.new_model.Sex.UNKNOWN)

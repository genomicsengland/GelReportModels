from protocols import participant_1_0_0
from protocols import participant_1_0_3
from protocols.migration import BaseMigration


class MigrationParticipants103To100(BaseMigration):
    old_model = participant_1_0_3
    new_model = participant_1_0_0

    def migrate_cancer_participant(self, cancer_participant):
        migrated_participant = self.new_model.CancerParticipant.fromJsonDict(cancer_participant.toJsonDict())

        migrated_participant.LDPCode = next((tumour_sample.LDPCode for tumour_sample in cancer_participant.tumourSamples), None)

        migrated_participant.primaryDiagnosisDisease = None
        if isinstance(cancer_participant.primaryDiagnosisDisease, list):
            migrated_participant.primaryDiagnosisDisease = ','.join(cancer_participant.primaryDiagnosisDisease)

        migrated_participant.primaryDiagnosisSubDisease = None
        if isinstance(cancer_participant.primaryDiagnosisSubDisease, list):
            migrated_participant.primaryDiagnosisSubDisease = ','.join(cancer_participant.primaryDiagnosisSubDisease)

        migrated_participant.assignedICD10 = None
        if isinstance(cancer_participant.assignedICD10, list):
            migrated_participant.assignedICD10 = ','.join(cancer_participant.assignedICD10)

        migrated_participant.tumourSamples = self.migrate_tumour_samples(
            tumour_samples=cancer_participant.tumourSamples
        )

        migrated_participant.germlineSamples = self.migrate_germline_samples(
            germline_samples=cancer_participant.germlineSamples
        )

        migrated_participant.matchedSamples = self.migrate_matched_samples(
            matched_samples=cancer_participant.matchedSamples
        )

        return self.validate_object(
            object_to_validate=migrated_participant, object_type=self.new_model.CancerParticipant
        )

    def migrate_matched_samples(self, matched_samples):
        return [self.migrate_matched_sample(matched_sample=matched_sample) for matched_sample in matched_samples]

    def migrate_matched_sample(self, matched_sample):
        return self.new_model.MatchedSamples().fromJsonDict(matched_sample.toJsonDict())

    def migrate_germline_samples(self, germline_samples):
        return [self.migrate_germline_sample(germline_sample=germline_sample) for germline_sample in germline_samples]

    def migrate_germline_sample(self, germline_sample):
        return self.new_model.GermlineSample().fromJsonDict(germline_sample.toJsonDict())

    def migrate_tumour_samples(self, tumour_samples):
        return [self.migrate_tumour_sample(tumour_sample=tumour_sample) for tumour_sample in tumour_samples]

    def migrate_tumour_sample(self, tumour_sample):
        """
        The tumourId will be migrated when the value can be parsed to an integer, otherwise it will be replaced
        by the labSampleId.
        :param tumour_sample:
        :return:
        """
        migrated_tumour_sample = self.new_model.TumourSample().fromJsonDict(
            jsonDict=tumour_sample.toJsonDict()
        )

        migrated_tumour_sample.tumourId = None
        if tumour_sample.tumourId is not None:
            try:
                migrated_tumour_sample.tumourId = int(tumour_sample.tumourId)
            except ValueError:
                migrated_tumour_sample.tumourId = tumour_sample.labSampleId

        migrated_tumour_sample.tumourType = tumour_sample.diseaseType
        migrated_tumour_sample.tumourSubType = tumour_sample.diseaseSubType
        migrated_tumour_sample.phase = tumour_sample.tumourType

        return self.validate_object(
            object_to_validate=migrated_tumour_sample, object_type=self.new_model.TumourSample
        )

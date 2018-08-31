from protocols import participant_1_0_0
from protocols import participant_1_0_3
from protocols.migration import BaseMigration


class MigrationParticipants103To100(BaseMigration):
    old_model = participant_1_0_3
    new_model = participant_1_0_0

    def migrate_cancer_participant(self, old_instance):
        """
        :type old_instance: participant_1_0_3.CancerParticipant
        :rtype:  participant_1_0_0.CancerParticipant
        """
        new_instance = self.convert_class(self.new_model.CancerParticipant, old_instance)
        if old_instance.tumourSamples is not None:
            new_instance.LDPCode = next((tumour_sample.LDPCode for tumour_sample in old_instance.tumourSamples), None)
        new_instance.primaryDiagnosisDisease = None
        if isinstance(old_instance.primaryDiagnosisDisease, list):
            new_instance.primaryDiagnosisDisease = ','.join(old_instance.primaryDiagnosisDisease)
        new_instance.primaryDiagnosisSubDisease = None
        if isinstance(old_instance.primaryDiagnosisSubDisease, list):
            new_instance.primaryDiagnosisSubDisease = ','.join(old_instance.primaryDiagnosisSubDisease)
        new_instance.assignedICD10 = None
        if isinstance(old_instance.assignedICD10, list):
            new_instance.assignedICD10 = ','.join(old_instance.assignedICD10)
        new_instance.tumourSamples = self.convert_collection(
            old_instance.tumourSamples, self._migrate_tumour_sample)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.CancerParticipant)

    def _migrate_tumour_sample(self, tumour_sample):
        new_instance = self.new_model.TumourSample().fromJsonDict(
            jsonDict=tumour_sample.toJsonDict()
        )
        new_instance.tumourId = None
        if tumour_sample.tumourId is not None:
            try:
                new_instance.tumourId = int(tumour_sample.tumourId)
            except ValueError:
                new_instance.tumourId = tumour_sample.labSampleId
        new_instance.tumourType = tumour_sample.diseaseType
        new_instance.tumourSubType = tumour_sample.diseaseSubType
        new_instance.phase = tumour_sample.tumourType
        return new_instance
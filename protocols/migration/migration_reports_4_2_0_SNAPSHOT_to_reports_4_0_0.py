from protocols import reports_4_0_0
from protocols import reports_4_2_0_SNAPSHOT
from protocols.migration import BaseMigration
from protocols.migration.participants import MigrationParticipants104SNAPSHOTTo100


class MigrateReports420SNAPSHOTTo400(BaseMigration):

    old_model = reports_4_2_0_SNAPSHOT
    new_model = reports_4_0_0

    def migrate_cancer_interpretation_request(self, cancer_interpretation_request):
        """
        :type cancer_interpretation_request: reports_4_2_0_SNAPSHOT.CancerInterpretationRequest
        :rtype: reports_4_0_0.CancerInterpretationRequest
        """
        new_cancer_interpretation_request = self.new_model.CancerInterpretationRequest.fromJsonDict(
            jsonDict=cancer_interpretation_request.toJsonDict()
        )

        new_cancer_participant = MigrationParticipants104SNAPSHOTTo100().migrate_cancer_participant(
            cancer_participant=cancer_interpretation_request.cancerParticipant
        )
        new_cancer_interpretation_request.cancerParticipant = new_cancer_participant

        return self.validate_object(
            object_to_validate=new_cancer_interpretation_request, object_type=self.new_model.CancerInterpretationRequest
        )

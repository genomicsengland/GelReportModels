from protocols import reports_6_0_1, reports_6_0_2
from protocols.migration import BaseMigration
from protocols.migration import migration_participant_112_to_participant_113



class MigrateReports601To602(BaseMigration):

    old_model = reports_6_0_1
    new_model = reports_6_0_2

    def migrate_interpretation_request_rd(self, old_instance):
        """
        Migrates a reports_6_0_1.InterpretationRequestRD into a reports_6_0_2.InterpretationRequestRD
        :type old_instance: reports_6_1.0.InterpretationRequestRD
        :rtype: reports_6_0_2.InterpretationRequestRD
        """
        new_instance = self.convert_class(target_klass=self.new_model.InterpretationRequestRD, instance=old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        participant_migration_class = migration_participant_112_to_participant_113.MigrateParticipant112To113()
        new_instance.pedigree = participant_migration_class.migrate_pedigree(old_pedigree=old_instance.pedigree)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD)

    def migrate_interpretation_request_cancer(self, old_instance):
        """
        Migrates a reports_6_0_1.CancerInterpretationRequest into a reports_6_0_2.CancerInterpretationRequest
        :type old_instance: reports_6_0_1.CancerInterpretationRequest
        :rtype: reports_6_0_2.CancerInterpretationRequest
        """
        new_instance = self.convert_class(target_klass=self.new_model.CancerInterpretationRequest, instance=old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        participant_migration_class = migration_participant_112_to_participant_113.MigrateParticipant112To113()
        new_instance.cancerParticipant = participant_migration_class.migrate_cancer_participant(
            old_cancer_participant=old_instance.cancerParticipant)
        return self.validate_object(object_to_validate=new_instance,
                                    object_type=self.new_model.CancerInterpretationRequest)

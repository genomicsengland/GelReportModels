from protocols import participant_1_0_3
from protocols import participant_1_1_0
from protocols.migration.base_migration import BaseMigration


class MigrateParticipant110To103(BaseMigration):

    old_model = participant_1_1_0
    new_model = participant_1_0_3

    def migrate_cancer_participant(self, old_participant):
        new_instance = self.convert_class(target_klass=self.new_model.CancerParticipant, instance=old_participant)
        new_instance.versionControl = self.new_model.VersionControl()
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.CancerParticipant)

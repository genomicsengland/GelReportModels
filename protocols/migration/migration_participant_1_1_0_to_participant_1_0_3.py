import logging

from protocols import participant_1_0_3
from protocols import participant_1_1_0
from protocols.migration.base_migration import BaseMigration
from protocols.migration.base_migration import MigrationError


class MigrateParticipant110To103(BaseMigration):

    old_model = participant_1_1_0
    new_model = participant_1_0_3

    def migrate_cancer_participant(self, old_participant):
        new_instance = self.convert_class(target_klass=self.new_model.CancerParticipant, instance=old_participant)
        new_instance.versionControl = self.new_model.VersionControl()
        new_instance.tumourSamples = self.migrate_tumour_samples(old_samples=old_participant.tumourSamples)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.CancerParticipant)

    def migrate_tumour_samples(self, old_samples):
        return [self.migrate_tumour_sample(old_sample=old_sample) for old_sample in old_samples]

    def migrate_tumour_sample(self, old_sample):
        new_instance = self.convert_class(target_klass=self.new_model.TumourSample, instance=old_sample)
        new_instance.morphologyICD = next((e for e in old_sample.morphologyICDs), "")
        new_instance.morphologySnomedCT = next((e for e in old_sample.morphologySnomedCTs), "")
        new_instance.morphologySnomedRT = next((e for e in old_sample.morphologySnomedRTs), "")
        new_instance.topographyICD = next((e for e in old_sample.topographyICDs), "")
        new_instance.topographySnomedCT = next((e for e in old_sample.topographySnomedCTs), "")
        new_instance.topographySnomedRT = next((e for e in old_sample.topographySnomedRTs), "")
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.TumourSample)

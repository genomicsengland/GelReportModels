from protocols import participant_1_0_3
from protocols import participant_1_1_0
from protocols.util import handle_avro_errors
from protocols.migration import BaseMigration
from protocols.migration.base_migration import MigrationError


class MigrationParticipants103To110(BaseMigration):
    old_model = participant_1_0_3
    new_model = participant_1_1_0

    def migrate_pedigree(self, old_instance):
        new_instance = self.convert_class(self.new_model.Pedigree, old_instance)
        if new_instance.validate(new_instance.toJsonDict()):
            return new_instance
        else:
            raise MigrationError(
                'This model can not be converted: ', handle_avro_errors(new_instance.validate_parts())
            )

    def migrate_cancer_participant(self, old_instance):
        """

        :param old_instance:
        :type old_instance: participants_1_0_3.CancerParticipant
        :return:
        """
        new_instance = self.convert_class(self.new_model.CancerParticipant, old_instance)   # type: participant_1_1_0.CancerParticipant
        new_instance.tumourSamples = self.convert_collection(old_instance.tumourSamples, self._migrate_tumour_sample)
        if new_instance.validate(new_instance.toJsonDict()):
            return new_instance
        else:
            raise MigrationError(
                'This model can not be converted: ', handle_avro_errors(new_instance.validate_parts())
            )

    def _migrate_tumour_sample(self, old_instance):
        """

        :param old_instance:
        :type old_instance: old_model.TumourSample
        :return:
        """
        new_instance = self.convert_class(self.new_model.TumourSample, old_instance)  # type: new_model.TumourSample

        if old_instance.morphologyICD is not None:
            new_instance.morphologyICDs = [old_instance.morphologyICD]
        if old_instance.morphologySnomedCT is not None:
            new_instance.morphologySnomedCTs = [old_instance.morphologySnomedCT]
        if old_instance.morphologySnomedRT is not None:
            new_instance.morphologySnomedRTs = [old_instance.morphologySnomedRT]
        if old_instance.topographyICD is not None:
            new_instance.topographyICDs = [old_instance.topographyICD]
        if old_instance.topographySnomedCT is not None:
            new_instance.topographySnomedCTs = [old_instance.topographySnomedCT]
        if old_instance.topographySnomedRT is not None:
            new_instance.topographySnomedRTs = [old_instance.topographySnomedRT]

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.TumourSample
        )
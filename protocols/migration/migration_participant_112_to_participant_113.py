from protocols import participant_1_1_2
from protocols import participant_1_1_3
from protocols.migration.base_migration import BaseMigration


class MigrateParticipant112To113(BaseMigration):

    old_model = participant_1_1_2
    new_model = participant_1_1_3

    def migrate_pedigree(self, old_pedigree):
        """
        :type old_pedigree: Participant 1.1.2 Pedigree
        :rtype: Participant 1.1.3 Pedigree
        """
        new_instance = self.convert_class(target_klass=self.new_model.Pedigree, instance=old_pedigree)
        new_instance.versionControl = self.new_model.VersionControl()
        new_instance.members = self.convert_collection(old_pedigree.members, self._migrate_pedigree_member)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Pedigree)

    def migrate_cancer_participant(self, old_cancer_participant):
        """
        :type old_cancer_participant: Participant 1.1.2 CancerParticipant
        :rtype: Participant 1_1_3 CancerParticipant
        """
        new_instance = self.convert_class(target_klass=self.new_model.CancerParticipant,
                                          instance=old_cancer_participant)
        new_instance.versionControl = self.new_model.VersionControl()
        new_instance.germlineSamples = self.convert_collection(old_cancer_participant.germlineSamples,
                                                               self._migrate_germline_sample)
        new_instance.tumourSamples = self.convert_collection(old_cancer_participant.tumourSamples,
                                                             self._migrate_tumour_sample)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.CancerParticipant)

    def _migrate_pedigree_member(self, old_pedigree_member):
        new_instance = self.convert_class(target_klass=self.new_model.PedigreeMember, instance=old_pedigree_member)
        new_instance.samples = self.convert_collection(old_pedigree_member.samples, self._migrate_germline_sample)
        return new_instance

    def _migrate_germline_sample(self, old_sample):
        new_instance = self.convert_class(target_klass=self.new_model.GermlineSample, instance=old_sample)
        new_instance.labSampleId = str(old_sample.labSampleId)
        return new_instance

    def _migrate_tumour_sample(self, old_sample):
        new_instance = self.convert_class(target_klass=self.new_model.TumourSample, instance=old_sample)
        new_instance.labSampleId = str(old_sample.labSampleId)
        return new_instance


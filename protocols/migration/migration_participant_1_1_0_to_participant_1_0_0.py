from protocols import participant_1_0_0
from protocols import participant_1_1_0
from protocols.migration.base_migration import BaseMigration


class MigrateParticipant110To100(BaseMigration):

    old_model = participant_1_1_0
    new_model = participant_1_0_0

    def migrate_pedigree(self, old_pedigree):
        """
        :param old_pedigree: Participant 1.1.0 Pedigree
        :return: Participant 1.0.0 Pedigree
        """
        new_instance = self.convert_class(target_klass=self.new_model.Pedigree, instance=old_pedigree)
        new_instance.versionControl = self.new_model.VersionControl()
        new_instance.members = self.convert_collection(old_pedigree.members, self.migrate_pedigree_member)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Pedigree)

    def migrate_pedigree_member(self, old_member):
        new_instance = self.convert_class(target_klass=self.new_model.PedigreeMember, instance=old_member)
        new_instance.disorderList = self.convert_collection(old_member.disorderList, self.migrate_disorder)
        new_instance.hpoTermList = self.convert_collection(old_member.hpoTermList, self.migrate_hpo_term)
        new_instance.samples = self.convert_collection(old_member.samples, self.migrate_sample)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.PedigreeMember)

    def migrate_sample(self, old_sample):
        new_instance = self.convert_class(target_klass=self.new_model.Sample, instance=old_sample)
        new_instance.source = self.migrate_sample_source(old_source=old_sample.source)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Sample)

    def migrate_sample_source(self, old_source):
        rd_sample_source_enum = [
            self.new_model.RDSampleSource.BLOOD, self.new_model.RDSampleSource.FIBROBLAST,
            self.new_model.RDSampleSource.SALIVA, self.new_model.RDSampleSource.TISSUE,
        ]
        return old_source if old_source in rd_sample_source_enum else None

    def migrate_disorder(self, old_disorder):
        new_instance = self.convert_class(target_klass=self.new_model.Disorder, instance=old_disorder)
        new_instance.ageOfOnset = str(old_disorder.ageOfOnset)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Disorder)

    def migrate_hpo_term(self, old_term):
        new_instance = self.convert_class(target_klass=self.new_model.HpoTerm, instance=old_term)
        new_instance.modifiers = self.migrate_hpo_term_modifiers(old_modifiers=old_term.modifiers)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.HpoTerm)

    @staticmethod
    def migrate_hpo_term_modifiers(old_modifiers):
        return dict(
            laterality=old_modifiers.laterality,
            progression=old_modifiers.progression,
            severity=old_modifiers.severity,
            spatial_pattern=old_modifiers.laterality,
        )

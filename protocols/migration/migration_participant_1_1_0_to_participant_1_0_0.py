import logging

from protocols import participant_1_0_0
from protocols import participant_1_1_0
from protocols.migration.base_migration import BaseMigration
from protocols.migration.base_migration import MigrationError


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
        new_instance.members = self.migrate_pedigree_members(old_members=old_pedigree.members)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Pedigree)

    def migrate_pedigree_members(self, old_members):
        return [self.migrate_pedigree_member(old_member=old_member) for old_member in old_members]

    def migrate_pedigree_member(self, old_member):
        new_instance = self.convert_class(target_klass=self.new_model.PedigreeMember, instance=old_member)
        new_instance.disorderList = self.migrate_disorders(old_disorders=old_member.disorderList)
        new_instance.hpoTermList = self.migrate_hpo_terms(old_terms=old_member.hpoTermList)
        new_instance.ancestries = self.migrate_ancestries(old_ancestries=old_member.ancestries)
        new_instance.samples = self.migrate_samples(old_samples=old_member.samples)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.PedigreeMember)

    def migrate_samples(self, old_samples):
        return None if old_samples is None else [self.migrate_sample(old_sample=old_sample) for old_sample in old_samples]

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

    def migrate_ancestries(self, old_ancestries):
        new_instance = self.convert_class(target_klass=self.new_model.Ancestries, instance=old_ancestries)
        new_instance.chiSquare1KGenomesPhase3Pop = self.migrate_chi_square_1k_genomes_phase_3_pop(
            old_chi_square_1k_genomes_phase_3_pop=old_ancestries.chiSquare1KGenomesPhase3Pop
        )
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Ancestries)

    def migrate_chi_square_1k_genomes_phase_3_pop(self, old_chi_square_1k_genomes_phase_3_pop):
        if old_chi_square_1k_genomes_phase_3_pop is None:
            return None
        return [self.migrate_cs1kgp3p(old_cs1kgp3p=old_cs1kgp3p) for old_cs1kgp3p in old_chi_square_1k_genomes_phase_3_pop]

    def migrate_cs1kgp3p(self, old_cs1kgp3p):
        new_instance = self.convert_class(target_klass=self.new_model.ChiSquare1KGenomesPhase3Pop, instance=old_cs1kgp3p)
        new_instance.kGSuperPopCategory = old_cs1kgp3p.kgSuperPopCategory
        new_instance.kGPopCategory = old_cs1kgp3p.kgPopCategory
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Ancestries)

    def migrate_disorders(self, old_disorders):
        return None if old_disorders is None else [self.migrate_disorder(old_disorder=old_disorder) for old_disorder in old_disorders]

    def migrate_disorder(self, old_disorder):
        new_instance = self.convert_class(target_klass=self.new_model.Disorder, instance=old_disorder)
        new_instance.ageOfOnset = str(old_disorder.ageOfOnset)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Disorder)

    def migrate_hpo_terms(self, old_terms):
        return None if old_terms is None else [self.migrate_hpo_term(old_term=old_term) for old_term in old_terms]

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

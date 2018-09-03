from protocols import participant_1_0_0
from protocols import participant_1_1_0
from protocols.migration.base_migration import BaseMigration


class MigrateParticipant110To100(BaseMigration):

    old_model = participant_1_1_0
    new_model = participant_1_0_0

    def migrate_pedigree(self, old_pedigree):
        """
        :type old_pedigree: Participant 1.1.0 Pedigree
        :rtype: Participant 1.0.0 Pedigree
        """
        new_instance = self.convert_class(target_klass=self.new_model.Pedigree, instance=old_pedigree)
        new_instance.versionControl = self.new_model.VersionControl()
        new_instance.members = self.convert_collection(old_pedigree.members, self._migrate_pedigree_member)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Pedigree)

    def migrate_cancer_participant(self, old_instance):
        """
        :type old_instance: participant_1_1_0.CancerParticipant
        :rtype:  participant_1_0_0.CancerParticipant
        """
        new_instance = self.convert_class(self.new_model.CancerParticipant, old_instance)
        new_instance.versionControl = self.new_model.VersionControl()
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

    def _migrate_pedigree_member(self, old_member):
        new_instance = self.convert_class(target_klass=self.new_model.PedigreeMember, instance=old_member)
        new_instance.disorderList = self.convert_collection(old_member.disorderList, self._migrate_disorder)
        new_instance.hpoTermList = self.convert_collection(old_member.hpoTermList, self._migrate_hpo_term)
        new_instance.samples = self.convert_collection(old_member.samples, self._migrate_sample)
        return new_instance

    def _migrate_sample(self, old_sample):
        new_instance = self.convert_class(target_klass=self.new_model.Sample, instance=old_sample)
        new_instance.source = self._migrate_sample_source(old_source=old_sample.source)
        return new_instance

    def _migrate_sample_source(self, old_source):
        rd_sample_source_enum = [
            self.new_model.RDSampleSource.BLOOD, self.new_model.RDSampleSource.FIBROBLAST,
            self.new_model.RDSampleSource.SALIVA, self.new_model.RDSampleSource.TISSUE,
        ]
        return old_source if old_source in rd_sample_source_enum else None

    def _migrate_disorder(self, old_disorder):
        new_instance = self.convert_class(target_klass=self.new_model.Disorder, instance=old_disorder)
        if old_disorder.ageOfOnset is not None:
            new_instance.ageOfOnset = str(old_disorder.ageOfOnset)
        return new_instance

    def _migrate_hpo_term(self, old_term):
        new_instance = self.convert_class(target_klass=self.new_model.HpoTerm, instance=old_term)
        new_instance.modifiers = self._migrate_hpo_term_modifiers(old_instance=old_term.modifiers)
        return new_instance

    @staticmethod
    def _migrate_hpo_term_modifiers(old_instance):
        if old_instance is None:
            return None
        new_instance = {}
        if old_instance.laterality:
            new_instance['laterality'] = old_instance.laterality
        if old_instance.progression:
            new_instance['progression'] = old_instance.progression
        if old_instance.severity:
            new_instance['severity'] = old_instance.severity
        if old_instance.spatialPattern:
            new_instance['spatialPattern'] = old_instance.spatialPattern
        return new_instance

import logging
from protocols import participant_1_0_0
from protocols import participant_1_0_3
from protocols.migration import BaseMigration


class MigrationParticipants100To103(BaseMigration):
    old_model = participant_1_0_0
    new_model = participant_1_0_3

    def migrate_pedigree(self, old_instance):
        """
        :type old_instance: participants_1_0_0.Pedigree
        :rtype: participants_1_0_3.Pedigree
        """
        new_instance = self.convert_class(self.new_model.Pedigree, old_instance)
        new_instance.versionControl = self.new_model.VersionControl()
        new_instance.members = self.convert_collection(old_instance.members, self._migrate_member)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Pedigree)

    def migrate_cancer_participant(self, old_instance):
        """
        :type old_instance: participants_1_0_0.CancerParticipant
        :rtype: participants_1_0_3.CancerParticipant
        """
        new_instance = self.convert_class(self.new_model.CancerParticipant, old_instance)
        new_instance.versionControl = self.new_model.VersionControl()
        new_instance.yearOfBirth = 0
        if old_instance.primaryDiagnosisDisease is not None:
            new_instance.primaryDiagnosisDisease = [old_instance.primaryDiagnosisDisease]
        if old_instance.primaryDiagnosisSubDisease is not None:
            new_instance.primaryDiagnosisSubDisease = [old_instance.primaryDiagnosisSubDisease]
        if old_instance.assignedICD10 is not None:
            new_instance.assignedICD10 = [old_instance.assignedICD10]
        new_instance.tumourSamples = self.convert_collection(
            old_instance.tumourSamples, self._migrate_tumour_sample, LDPCode=old_instance.LDPCode or "")
        new_instance.germlineSamples = self.convert_collection(
            old_instance.germlineSamples, self._migrate_germline_sample, LDPCode=old_instance.LDPCode or "")
        new_instance.matchedSamples = self.convert_collection(
            old_instance.matchedSamples, lambda s: self.convert_class(self.new_model.MatchedSamples, s),
            default=[self.new_model.MatchedSamples()])
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.CancerParticipant)

    def _migrate_tumour_sample(self, tumour_sample, LDPCode):
        new_instance = self.convert_class(self.new_model.TumourSample, tumour_sample)
        new_instance.LDPCode = LDPCode
        new_instance.tumourId = str(tumour_sample.tumourId)
        new_instance.diseaseType = tumour_sample.tumourType
        new_instance.diseaseSubType = tumour_sample.tumourSubType
        new_instance.tumourType = tumour_sample.phase
        return new_instance

    def _migrate_germline_sample(self, germline_sample, LDPCode):
        new_instance = self.convert_class(self.new_model.GermlineSample, germline_sample)
        new_instance.LDPCode = LDPCode
        return new_instance

    def _migrate_member(self, old_member):
        new_instance = self.convert_class(self.new_model.PedigreeMember, old_member)
        new_instance.disorderList = self.convert_collection(old_member.disorderList, self._migrate_disorder)
        new_instance.hpoTermList = self.convert_collection(old_member.hpoTermList, self._migrate_hpo_term)
        return new_instance

    def _migrate_disorder(self, old_instance):
        new_instance = self.convert_class(self.new_model.Disorder, old_instance)
        new_instance.ageOfOnset = self.convert_string_to_float(old_instance.ageOfOnset, fail=False)
        return new_instance

    def _migrate_hpo_term(self, old_instance):
        if old_instance.ageOfOnset:
            old_instance.ageOfOnset = old_instance.ageOfOnset.upper().replace(" ", "_")
        new_instance = self.convert_class(self.new_model.HpoTerm, old_instance)
        values = [
            self.new_model.AgeOfOnset.EMBRYONAL_ONSET,
            self.new_model.AgeOfOnset.FETAL_ONSET,
            self.new_model.AgeOfOnset.NEONATAL_ONSET,
            self.new_model.AgeOfOnset.INFANTILE_ONSET,
            self.new_model.AgeOfOnset.CHILDHOOD_ONSET,
            self.new_model.AgeOfOnset.JUVENILE_ONSET,
            self.new_model.AgeOfOnset.YOUNG_ADULT_ONSET,
            self.new_model.AgeOfOnset.LATE_ONSET,
            self.new_model.AgeOfOnset.MIDDLE_AGE_ONSET
        ]
        if old_instance.ageOfOnset not in values:
            new_instance.ageOfOnset = None
            if old_instance.ageOfOnset:
                logging.warning("Lost value for 'ageOfOnset={}' during migration".format(old_instance.ageOfOnset))
        if old_instance.modifiers is not None:
            new_modifiers = self.new_model.HpoTermModifiers()
            for name, value in old_instance.modifiers.items():
                if name == "laterality" and value in [self.new_model.Laterality.RIGHT,
                                                      self.new_model.Laterality.UNILATERAL,
                                                      self.new_model.Laterality.BILATERAL,
                                                      self.new_model.Laterality.LEFT]:
                    new_modifiers.laterality = value
                elif name == "progression" and value in [self.new_model.Progression.PROGRESSIVE,
                                                         self.new_model.Progression.NONPROGRESSIVE]:
                    new_modifiers.progression = value
                elif name == "severity" and value in [self.new_model.Severity.BORDERLINE,
                                                      self.new_model.Severity.MILD,
                                                      self.new_model.Severity.MODERATE,
                                                      self.new_model.Severity.SEVERE,
                                                      self.new_model.Severity.PROFOUND]:
                    new_modifiers.severity = value
                elif name == "spatialPattern" and value in [self.new_model.SpatialPattern.DISTAL,
                                                            self.new_model.SpatialPattern.GENERALIZED,
                                                            self.new_model.SpatialPattern.LOCALIZED,
                                                            self.new_model.SpatialPattern.PROXIMAL]:
                    new_modifiers.spatialPattern = value
                else:
                    logging.warning("Lost modifier '{}={}' during migration".format(name, value))
            new_instance.modifiers = new_modifiers
        return new_instance

import logging
from protocols import participant_1_0_0
from protocols import participant_1_0_3
from protocols.util import handle_avro_errors
from protocols.migration import BaseMigration


class MigrationParticipants100To103(BaseMigration):
    old_model = participant_1_0_0
    new_model = participant_1_0_3

    def migrate_cancer_participant(self, cancer_participant):
        migrated_participant = self.convert_class(self.new_model.CancerParticipant, cancer_participant)

        migrated_participant.versionControl = self.new_model.VersionControl()
        migrated_participant.yearOfBirth = 0

        if cancer_participant.primaryDiagnosisDisease is not None:
            migrated_participant.primaryDiagnosisDisease = [cancer_participant.primaryDiagnosisDisease]

        if cancer_participant.primaryDiagnosisSubDisease is not None:
            migrated_participant.primaryDiagnosisSubDisease = [cancer_participant.primaryDiagnosisSubDisease]

        if cancer_participant.assignedICD10 is not None:
            migrated_participant.assignedICD10 = [cancer_participant.assignedICD10]

        migrated_participant.tumourSamples = self.convert_collection(
            cancer_participant.tumourSamples, self.migrate_tumour_sample, LDPCode=cancer_participant.LDPCode)
        migrated_participant.germlineSamples = self.convert_collection(
            cancer_participant.germlineSamples, self.migrate_germline_sample, LDPCode=cancer_participant.LDPCode)
        migrated_participant.matchedSamples = self.convert_collection(
            cancer_participant.matchedSamples, lambda s: self.convert_class(self.new_model.MatchedSamples, s),
            default=[self.new_model.MatchedSamples()])

        return self.validate_object(
            object_to_validate=migrated_participant, object_type=self.new_model.CancerParticipant
        )

    def migrate_tumour_sample(self, tumour_sample, LDPCode):
        migrated_tumour_sample = self.convert_class(self.new_model.TumourSample, tumour_sample)
        migrated_tumour_sample.LDPCode = LDPCode
        migrated_tumour_sample.tumourId = str(tumour_sample.tumourId)
        migrated_tumour_sample.diseaseType = tumour_sample.tumourType
        migrated_tumour_sample.diseaseSubType = tumour_sample.tumourSubType
        migrated_tumour_sample.tumourType = tumour_sample.phase

        return self.validate_object(
            object_to_validate=migrated_tumour_sample, object_type=self.new_model.TumourSample
        )

    def migrate_germline_sample(self, germline_sample, LDPCode):
        migrated_germline_sample = self.convert_class(self.new_model.GermlineSample, germline_sample)

        migrated_germline_sample.LDPCode = LDPCode

        return self.validate_object(
            object_to_validate=migrated_germline_sample, object_type=self.new_model.GermlineSample
        )

    def migrate_pedigree(self, old_pedigree):
        new_pedigree = self.convert_class(self.new_model.Pedigree, old_pedigree)
        new_pedigree.versionControl = self.new_model.VersionControl()

        new_pedigree.members = self.convert_collection(old_pedigree.members, self.migrate_member)

        if new_pedigree.validate(new_pedigree.toJsonDict()):
            return new_pedigree
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(new_pedigree.validate_parts())
            )

    def migrate_member(self, old_member):
        new_member = self.convert_class(self.new_model.PedigreeMember, old_member)
        new_member.disorderList = self.convert_collection(old_member.disorderList, self.migrate_disorder)
        new_member.hpoTermList = self.convert_collection(old_member.hpoTermList, self.migrate_hpo_term)
        if new_member.validate(new_member.toJsonDict(), verbose=True):
            return new_member
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(new_member.validate_parts())
            )

    def migrate_disorder(self, old_instance):
        new_instance = self.convert_class(self.new_model.Disorder, old_instance)
        new_instance.ageOfOnset = self.convert_string_to_float(old_instance.ageOfOnset, fail=False)
        return new_instance

    def migrate_hpo_term(self, old_instance):
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
            for name, value in old_instance.modifiers.items():
                new_modifiers = self.new_model.HpoTermModifiers()
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
                    new_modifiers.severity = value
                else:
                    logging.warning("Lost modifier '{}={}' during migration".format(name, value))
                new_instance.modifiers = new_modifiers

        return new_instance
from protocols import reports_3_0_0 as participant_old
from protocols import participant_1_0_0
from protocols import participant_1_0_1
from protocols import participant_1_0_3
from protocols.migration import BaseMigration


class MigrationParticipants101ToReports(BaseMigration):
    old_model = participant_1_0_1
    new_model = participant_old

    def migrate_pedigree(self, pedigree):
        """
        :type pedigree: participant_1_0_1.Pedigree
        :rtype: participant_old.Pedigree
        """
        new_instance = self.convert_class(self.new_model.Pedigree, pedigree)
        new_instance.versionControl = self.new_model.VersionControl()
        new_instance.gelFamilyId = pedigree.familyId
        new_instance.participants = self.convert_collection(
            pedigree.members, self._migrate_pedigree_member, family_id=new_instance.gelFamilyId)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Pedigree)

    def _migrate_pedigree_member(self, member, family_id):
        new_instance = self.convert_class(self.new_model.RDParticipant, member)
        new_instance.versionControl = participant_old.VersionControl()
        new_instance.gelId = str(member.participantId)
        new_instance.gelFamilyId = family_id
        new_instance.sex = self._migrate_enumerations('Sex', member.sex)
        new_instance.lifeStatus = self._migrate_enumerations('LifeStatus', member.lifeStatus)
        new_instance.adoptedStatus = self._migrate_enumerations('AdoptedStatus', member.adoptedStatus)
        new_instance.affectionStatus = self._migrate_enumerations('AffectionStatus', member.affectionStatus)
        if new_instance.affectionStatus == 'uncertain':
            new_instance.affectionStatus = 'unknown'
        new_instance.hpoTermList = self.convert_collection(member.hpoTermList, self._migrate_hpo_terms, default=[])
        if member.yearOfBirth is not None:
            new_instance.yearOfBirth = str(member.yearOfBirth)
        new_instance.samples = self.convert_collection(member.samples, lambda s: s.sampleId, default=[])
        new_instance.disorderList = self.convert_collection(
            member.disorderList, self._migrate_disorders, default=[])

        if member.ancestries is None:
            new_instance.ancestries = participant_old.Ancestries()
        return new_instance

    def _migrate_enumerations(self, etype, value):
        if etype in ['LifeStatus', 'AffectionStatus']:
            return value.lower()
        elif etype == 'Sex':
            return {'MALE': 'male', 'FEMALE': 'female', 'UNKNOWN': 'unknown'}.get(value)
        elif etype == 'AdoptedStatus':
            return {'notadopted': 'not_adopted', 'adoptedin': 'adoptedin', 'adoptedout': 'adoptedout'}.get(value)
        elif etype == 'termPresence':
            return {'yes': True, 'no': False, 'unknown': None}.get(value)
        else:
            raise NotImplementedError(etype + ' is not a valid enumeration type or is not implemented')

    def _migrate_hpo_terms(self, hpo_term):
        new_instance = self.convert_class(self.new_model.HpoTerm, hpo_term)
        new_instance.termPresence = self._migrate_enumerations('termPresence', hpo_term.termPresence)
        if hpo_term.modifiers:
            mod_as_json = hpo_term.modifiers.toJsonDict()
        else:
            mod_as_json = {}
        new_instance.modifiers = {k: mod_as_json[k] for k in mod_as_json if mod_as_json[k]}
        return new_instance

    def _migrate_disorders(self, disorder):
        new_instance = self.convert_class(self.new_model.Disorder, disorder)
        if disorder.ageOfOnset is not None:
            new_instance.ageOfOnset = str(disorder.ageOfOnset)
        return new_instance


class MigrationParticipants103To100(BaseMigration):
    old_model = participant_1_0_3
    new_model = participant_1_0_0

    def migrate_cancer_participant(self, old_instance):
        """
        :type old_instance: participant_1_0_3.CancerParticipant
        :rtype:  participant_1_0_0.CancerParticipant
        """
        new_instance = self.convert_class(self.new_model.CancerParticipant, old_instance)
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


class MigrationParticipants100ToReports(BaseMigration):
    old_model = participant_1_0_0
    new_model = participant_old

    def migrate_pedigree(self, old_instance):
        """
        :param old_instance: org.gel.models.participant.avro.Pedigree 1.0.0
        :rtype: org.gel.models.report.avro RDParticipant.Pedigree 3.0.0
        """
        new_instance = self.convert_class(self.new_model.Pedigree, old_instance)
        new_instance.versionControl = self.new_model.VersionControl()
        new_instance.gelFamilyId = old_instance.familyId
        new_instance.participants = self.convert_collection(
            old_instance.members, self._migrate_member_to_participant, family_id=old_instance.familyId)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Pedigree)

    def _migrate_member_to_participant(self, old_member, family_id):
        new_instance = self.convert_class(self.new_model.RDParticipant, old_member)
        new_instance.gelFamilyId = family_id
        new_instance.pedigreeId = old_member.pedigreeId or 0
        new_instance.isProband = old_member.isProband or False
        new_instance.gelId = old_member.participantId
        new_instance.sex = self._migrate_sex(old_sex=old_member.sex)
        new_instance.personKaryotipicSex = self._migrate_person_karyotypic_sex(old_pks=old_member.personKaryotypicSex)
        if old_member.yearOfBirth is not None:
            new_instance.yearOfBirth = str(old_member.yearOfBirth)
        new_instance.adoptedStatus = self._migrate_adopted_status(old_status=old_member.adoptedStatus)
        new_instance.lifeStatus = self._migrate_life_status(old_status=old_member.lifeStatus)
        new_instance.affectionStatus = self._migrate_affection_status(old_status=old_member.affectionStatus)
        new_instance.hpoTermList = self.convert_collection(
            old_member.hpoTermList, self._migrate_hpo_term, default=[])
        new_instance.samples = self.convert_collection(old_member.samples, lambda s: s .sampleId)
        new_instance.versionControl = self.new_model.VersionControl()
        if old_member.consentStatus is None:
            new_instance.consentStatus = self.new_model.ConsentStatus(
                programmeConsent=True, primaryFindingConsent=True, secondaryFindingConsent=True,
                carrierStatusConsent=True
            )
        if old_member.ancestries is None:
            new_instance.ancestries = self.new_model.Ancestries()
        if old_member.consanguineousParents is None:
            new_instance.consanguineousParents = self.new_model.TernaryOption.unknown
        if new_instance.disorderList is None:
            new_instance.disorderList = []
        return new_instance

    def _migrate_hpo_term(self, old_term):
        new_instance = self.convert_class(target_klass=self.new_model.HpoTerm, instance=old_term)
        new_instance.termPresence = self._migrate_ternary_option_to_boolean(ternary_option=old_term.termPresence)
        return new_instance

    def _migrate_ternary_option_to_boolean(self, ternary_option):
        ternary_map = {
            self.old_model.TernaryOption.no: False,
            self.old_model.TernaryOption.yes: True,
        }
        return ternary_map.get(ternary_option, None)

    def _migrate_affection_status(self, old_status):
        status_map = {
            self.old_model.AffectionStatus.AFFECTED: self.new_model.AffectionStatus.affected,
            self.old_model.AffectionStatus.UNAFFECTED: self.new_model.AffectionStatus.unaffected,
            self.old_model.AffectionStatus.UNCERTAIN: self.new_model.AffectionStatus.unknown,
        }
        return status_map.get(old_status, self.new_model.AffectionStatus.unknown)

    def _migrate_life_status(self, old_status):
        status_map = {
            self.old_model.LifeStatus.ABORTED: self.new_model.LifeStatus.aborted,
            self.old_model.LifeStatus.ALIVE: self.new_model.LifeStatus.alive,
            self.old_model.LifeStatus.DECEASED: self.new_model.LifeStatus.deceased,
            self.old_model.LifeStatus.UNBORN: self.new_model.LifeStatus.unborn,
            self.old_model.LifeStatus.STILLBORN: self.new_model.LifeStatus.stillborn,
            self.old_model.LifeStatus.MISCARRIAGE: self.new_model.LifeStatus.miscarriage,
        }
        return status_map.get(old_status, self.new_model.LifeStatus.alive)

    def _migrate_adopted_status(self, old_status):
        status_map = {
            self.old_model.AdoptedStatus.notadopted: self.new_model.AdoptedStatus.not_adopted,
            self.old_model.AdoptedStatus.adoptedin: self.new_model.AdoptedStatus.adoptedin,
            self.old_model.AdoptedStatus.adoptedout: self.new_model.AdoptedStatus.adoptedout,
        }
        return status_map.get(old_status, self.new_model.AdoptedStatus.not_adopted)

    def _migrate_person_karyotypic_sex(self, old_pks):
        pks_map = {
            self.old_model.PersonKaryotipicSex.UNKNOWN: self.new_model.PersonKaryotipicSex.unknown,
            self.old_model.PersonKaryotipicSex.XX: self.new_model.PersonKaryotipicSex.XX,
            self.old_model.PersonKaryotipicSex.XY: self.new_model.PersonKaryotipicSex.XY,
            self.old_model.PersonKaryotipicSex.XO: self.new_model.PersonKaryotipicSex.XO,
            self.old_model.PersonKaryotipicSex.XXY: self.new_model.PersonKaryotipicSex.XXY,
            self.old_model.PersonKaryotipicSex.XXX: self.new_model.PersonKaryotipicSex.XXX,
            self.old_model.PersonKaryotipicSex.XXYY: self.new_model.PersonKaryotipicSex.XXYY,
            self.old_model.PersonKaryotipicSex.XXXY: self.new_model.PersonKaryotipicSex.XXXY,
            self.old_model.PersonKaryotipicSex.XXXX: self.new_model.PersonKaryotipicSex.XXXX,
            self.old_model.PersonKaryotipicSex.XYY: self.new_model.PersonKaryotipicSex.XYY,
            self.old_model.PersonKaryotipicSex.OTHER: self.new_model.PersonKaryotipicSex.other,
        }
        return pks_map.get(old_pks)

    def _migrate_sex(self, old_sex):
        sex_map = {
            self.old_model.Sex.MALE: self.new_model.Sex.male,
            self.old_model.Sex.FEMALE: self.new_model.Sex.female,
            self.old_model.Sex.UNKNOWN: self.new_model.Sex.unknown,
        }
        return sex_map.get(old_sex, self.new_model.Sex.undetermined)

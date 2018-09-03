from protocols import reports_3_0_0 as participant_old
from protocols import participant_1_0_1
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
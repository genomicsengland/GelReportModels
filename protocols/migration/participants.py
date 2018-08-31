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
        new_pedigree = self.convert_class(self.new_model.Pedigree, pedigree)
        new_pedigree.versionControl = self.new_model.VersionControl()
        new_pedigree.analysisPanels = self.convert_collection(pedigree.analysisPanels, self.migrate_analysis_panel)
        new_pedigree.gelFamilyId = pedigree.familyId
        new_pedigree.participants = self.convert_collection(
            pedigree.members, self.migrate_pedigree_member, family_id=new_pedigree.gelFamilyId)
        if new_pedigree.validate(new_pedigree.toJsonDict()):
            return new_pedigree
        else:
            raise Exception('This model can not be converted')

    def migrate_pedigree_member(self, member, family_id):
        """

        :type member: participant_1_0_1.PedigreeMember
        :rtype: participant_old.RDParticipant
        """
        new_pedigree_member = self.convert_class(self.new_model.RDParticipant, member)
        new_pedigree_member.versionControl = participant_old.VersionControl()
        new_pedigree_member.gelId = str(member.participantId)
        new_pedigree_member.gelFamilyId = family_id
        new_pedigree_member.sex = self.migrate_enumerations('Sex', member.sex)
        new_pedigree_member.lifeStatus = self.migrate_enumerations('LifeStatus', member.lifeStatus)
        new_pedigree_member.adoptedStatus = self.migrate_enumerations('AdoptedStatus', member.adoptedStatus)
        new_pedigree_member.affectionStatus = self.migrate_enumerations('AffectionStatus', member.affectionStatus)
        if new_pedigree_member.affectionStatus == 'uncertain':
            new_pedigree_member.affectionStatus = 'unknown'
        new_pedigree_member.hpoTermList = self.convert_collection(member.hpoTermList, self.migrate_hpo_terms, default=[])
        if member.yearOfBirth is not None:
            new_pedigree_member.yearOfBirth = str(member.yearOfBirth)
        new_pedigree_member.samples = self.convert_collection(member.samples, lambda s: s.sampleId, default=[])
        new_pedigree_member.disorderList = self.convert_collection(
            member.disorderList, self.migrate_disorders, default=[])

        if member.ancestries is None:
            new_pedigree_member.ancestries = participant_old.Ancestries()

        if new_pedigree_member.validate(new_pedigree_member.toJsonDict()):
            return new_pedigree_member
        else:
            raise Exception('This model can not be converted')

    def migrate_enumerations(self, etype, value):
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

    def migrate_hpo_terms(self, hpo_term):
        """

        :type hpo_term: participant_1_0_1.HpoTerm
        :rtype: participant_old.HpoTerm
        """
        new_hpo = self.convert_class(self.new_model.HpoTerm, hpo_term)
        new_hpo.termPresence = self.migrate_enumerations('termPresence', hpo_term.termPresence)
        if hpo_term.modifiers:
            mod_as_json = hpo_term.modifiers.toJsonDict()
        else:
            mod_as_json = {}
        new_hpo.modifiers = {k: mod_as_json[k] for k in mod_as_json if mod_as_json[k]}
        if new_hpo.validate(new_hpo.toJsonDict()):
            return new_hpo
        else:
            raise Exception('This model can not be converted')

    def migrate_disorders(self, disorder):
        """

        :type disorder: participant_1_0_1.Disorder
        :rtype: participant_old.Disorder
        """
        new_disorder = self.convert_class(self.new_model.Disorder, disorder)
        if disorder.ageOfOnset is not None:
            new_disorder.ageOfOnset = str(disorder.ageOfOnset)
        if new_disorder.validate(new_disorder.toJsonDict()):
            return new_disorder
        else:
            raise Exception('This model can not be converted')

    def migrate_analysis_panel(self, analysis_panel):
        """

        :type analysis_panel: participant_1_0_1.AnalysisPanel
        :rtype: participant_old.AnalysisPanel
        """

        new_analysis_panel = self.convert_class(self.new_model.AnalysisPanel, analysis_panel)
        new_analysis_panel.multiple_genetic_origins = analysis_panel.multipleGeneticOrigins
        new_analysis_panel.review_outcome = analysis_panel.reviewOutcome
        if new_analysis_panel.validate(new_analysis_panel.toJsonDict()):
            return new_analysis_panel
        else:
            raise Exception('This model can not be converted')


class MigrationParticipants103To100(BaseMigration):
    old_model = participant_1_0_3
    new_model = participant_1_0_0

    def migrate_cancer_participant(self, cancer_participant):
        migrated_participant = self.convert_class(self.new_model.CancerParticipant, cancer_participant)

        if cancer_participant.tumourSamples is not None:
            migrated_participant.LDPCode = next((tumour_sample.LDPCode for tumour_sample in cancer_participant.tumourSamples), None)

        migrated_participant.primaryDiagnosisDisease = None
        if isinstance(cancer_participant.primaryDiagnosisDisease, list):
            migrated_participant.primaryDiagnosisDisease = ','.join(cancer_participant.primaryDiagnosisDisease)

        migrated_participant.primaryDiagnosisSubDisease = None
        if isinstance(cancer_participant.primaryDiagnosisSubDisease, list):
            migrated_participant.primaryDiagnosisSubDisease = ','.join(cancer_participant.primaryDiagnosisSubDisease)

        migrated_participant.assignedICD10 = None
        if isinstance(cancer_participant.assignedICD10, list):
            migrated_participant.assignedICD10 = ','.join(cancer_participant.assignedICD10)

        migrated_participant.tumourSamples = self.convert_collection(
            cancer_participant.tumourSamples, self.migrate_tumour_sample)

        return self.validate_object(
            object_to_validate=migrated_participant, object_type=self.new_model.CancerParticipant
        )

    def migrate_tumour_sample(self, tumour_sample):
        """
        The tumourId will be migrated when the value can be parsed to an integer, otherwise it will be replaced
        by the labSampleId.
        :param tumour_sample:
        :return:
        """
        migrated_tumour_sample = self.new_model.TumourSample().fromJsonDict(
            jsonDict=tumour_sample.toJsonDict()
        )

        migrated_tumour_sample.tumourId = None
        if tumour_sample.tumourId is not None:
            try:
                migrated_tumour_sample.tumourId = int(tumour_sample.tumourId)
            except ValueError:
                migrated_tumour_sample.tumourId = tumour_sample.labSampleId

        migrated_tumour_sample.tumourType = tumour_sample.diseaseType
        migrated_tumour_sample.tumourSubType = tumour_sample.diseaseSubType
        migrated_tumour_sample.phase = tumour_sample.tumourType

        return self.validate_object(
            object_to_validate=migrated_tumour_sample, object_type=self.new_model.TumourSample
        )


class MigrationParticipants100ToReports(BaseMigration):
    old_model = participant_1_0_0
    new_model = participant_old

    def migrate_pedigree(self, old_pedigree):
        """
        :param old_pedigree: org.gel.models.participant.avro.Pedigree 1.0.0
        :return: org.gel.models.report.avro RDParticipant.Pedigree 3.0.0
        """
        new_pedigree = self.convert_class(self.new_model.Pedigree, old_pedigree)
        new_pedigree.versionControl = self.new_model.VersionControl()
        new_pedigree.gelFamilyId = old_pedigree.familyId
        new_pedigree.analysisPanels = self.convert_collection(
            old_pedigree.analysisPanels, self.migrate_analysis_panel)
        new_pedigree.participants = self.convert_collection(
            old_pedigree.members, self.migrate_member_to_participant, family_id=old_pedigree.familyId)
        return self.validate_object(object_to_validate=new_pedigree, object_type=self.new_model.Pedigree)

    def migrate_member_to_participant(self, old_member, family_id):
        new_participant = self.convert_class(self.new_model.RDParticipant, old_member)
        new_participant.gelFamilyId = family_id
        new_participant.pedigreeId = old_member.pedigreeId or 0
        new_participant.isProband = old_member.isProband or False
        new_participant.gelId = old_member.participantId
        new_participant.sex = self.migrate_sex(old_sex=old_member.sex)
        new_participant.personKaryotipicSex = self.migrate_person_karyotypic_sex(old_pks=old_member.personKaryotypicSex)
        if old_member.yearOfBirth is not None:
            new_participant.yearOfBirth = str(old_member.yearOfBirth)
        new_participant.adoptedStatus = self.migrate_adopted_status(old_status=old_member.adoptedStatus)
        new_participant.lifeStatus = self.migrate_life_status(old_status=old_member.lifeStatus)
        new_participant.affectionStatus = self.migrate_affection_status(old_status=old_member.affectionStatus)
        new_participant.hpoTermList = self.convert_collection(
            old_member.hpoTermList, self.migrate_hpo_term, default=[])
        new_participant.samples = self.convert_collection(old_member.samples, lambda s: s .sampleId)
        new_participant.versionControl = self.new_model.VersionControl()
        if old_member.consentStatus is None:
            new_participant.consentStatus = self.new_model.ConsentStatus(
                programmeConsent=True, primaryFindingConsent=True, secondaryFindingConsent=True,
                carrierStatusConsent=True
            )
        if old_member.ancestries is None:
            new_participant.ancestries = self.new_model.Ancestries()
        if old_member.consanguineousParents is None:
            new_participant.consanguineousParents = self.new_model.TernaryOption.unknown
        if new_participant.disorderList is None:
            new_participant.disorderList = []

        return self.validate_object(object_to_validate=new_participant, object_type=self.new_model.RDParticipant)

    def migrate_hpo_term(self, old_term):
        new_term = self.convert_class(target_klass=self.new_model.HpoTerm, instance=old_term)
        new_term.termPresence = self.migrate_ternary_option_to_boolean(ternary_option=old_term.termPresence)
        return self.validate_object(object_to_validate=new_term, object_type=self.new_model.HpoTerm)

    def migrate_ternary_option_to_boolean(self, ternary_option):
        ternary_map = {
            self.old_model.TernaryOption.no: False,
            self.old_model.TernaryOption.yes: True,
        }
        return ternary_map.get(ternary_option, None)

    def migrate_affection_status(self, old_status):
        status_map = {
            self.old_model.AffectionStatus.AFFECTED: self.new_model.AffectionStatus.affected,
            self.old_model.AffectionStatus.UNAFFECTED: self.new_model.AffectionStatus.unaffected,
            self.old_model.AffectionStatus.UNCERTAIN: self.new_model.AffectionStatus.unknown,
        }
        return status_map.get(old_status, self.new_model.AffectionStatus.unknown)

    def migrate_life_status(self, old_status):
        status_map = {
            self.old_model.LifeStatus.ABORTED: self.new_model.LifeStatus.aborted,
            self.old_model.LifeStatus.ALIVE: self.new_model.LifeStatus.alive,
            self.old_model.LifeStatus.DECEASED: self.new_model.LifeStatus.deceased,
            self.old_model.LifeStatus.UNBORN: self.new_model.LifeStatus.unborn,
            self.old_model.LifeStatus.STILLBORN: self.new_model.LifeStatus.stillborn,
            self.old_model.LifeStatus.MISCARRIAGE: self.new_model.LifeStatus.miscarriage,
        }
        return status_map.get(old_status, self.new_model.LifeStatus.alive)

    def migrate_adopted_status(self, old_status):
        status_map = {
            self.old_model.AdoptedStatus.notadopted: self.new_model.AdoptedStatus.not_adopted,
            self.old_model.AdoptedStatus.adoptedin: self.new_model.AdoptedStatus.adoptedin,
            self.old_model.AdoptedStatus.adoptedout: self.new_model.AdoptedStatus.adoptedout,
        }
        return status_map.get(old_status, self.new_model.AdoptedStatus.not_adopted)

    def migrate_person_karyotypic_sex(self, old_pks):
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

    def migrate_sex(self, old_sex):
        sex_map = {
            self.old_model.Sex.MALE: self.new_model.Sex.male,
            self.old_model.Sex.FEMALE: self.new_model.Sex.female,
            self.old_model.Sex.UNKNOWN: self.new_model.Sex.unknown,
        }
        return sex_map.get(old_sex, self.new_model.Sex.undetermined)

    def migrate_analysis_panel(self, old_panel):
        new_panel = self.convert_class(self.new_model.AnalysisPanel, old_panel)
        new_panel.review_outcome = old_panel.reviewOutcome
        new_panel.multiple_genetic_origins = old_panel.multipleGeneticOrigins
        return self.validate_object(object_to_validate=new_panel, object_type=self.new_model.AnalysisPanel)

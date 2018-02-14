from protocols import reports_3_0_0 as participant_old
from protocols import participant_1_0_0
from protocols import participant_1_0_3
from protocols.util import handle_avro_errors
from protocols.migration import BaseMigration


class MigrationParticipants100To103(BaseMigration):
    old_model = participant_1_0_0
    new_model = participant_1_0_3

    def migrate_cancer_participant(self, cancer_participant):
        migrated_participant = self.new_model.CancerParticipant.fromJsonDict(cancer_participant.toJsonDict())

        migrated_participant.versionControl = self.new_model.VersionControl()

        migrated_participant.yearOfBirth = 0

        if cancer_participant.primaryDiagnosisDisease is not None:
            migrated_participant.primaryDiagnosisDisease = [cancer_participant.primaryDiagnosisDisease]

        if cancer_participant.primaryDiagnosisSubDisease is not None:
            migrated_participant.primaryDiagnosisSubDisease = [cancer_participant.primaryDiagnosisSubDisease]

        if cancer_participant.assignedICD10 is not None:
            migrated_participant.assignedICD10 = [cancer_participant.assignedICD10]

        migrated_participant.tumourSamples = self.migrate_tumour_samples(
            tumour_samples=cancer_participant.tumourSamples, LDPCode=cancer_participant.LDPCode
        )
        migrated_participant.germlineSamples = self.migrate_germline_samples(
            germline_samples=cancer_participant.germlineSamples, LDPCode=cancer_participant.LDPCode
        )
        migrated_participant.matchedSamples = self.migrate_matched_samples(
            matched_samples=cancer_participant.matchedSamples
        )

        return self.validate_object(
            object_to_validate=migrated_participant, object_type=self.new_model.CancerParticipant
        )

    def migrate_matched_samples(self, matched_samples):
        if matched_samples is None:
            ms = self.new_model.MatchedSamples()
            return [ms]
        return [self.migrate_matched_sample(matched_sample=matched_sample) for matched_sample in matched_samples]

    def migrate_matched_sample(self, matched_sample):
        return self.new_model.MatchedSamples().fromJsonDict(jsonDict=matched_sample.toJsonDict())

    def migrate_tumour_sample(self, tumour_sample, LDPCode):
        migrated_tumour_sample = self.new_model.TumourSample.fromJsonDict(tumour_sample.toJsonDict())

        migrated_tumour_sample.LDPCode = LDPCode
        migrated_tumour_sample.tumourId = str(tumour_sample.tumourId)
        migrated_tumour_sample.diseaseType = tumour_sample.tumourType
        migrated_tumour_sample.diseaseSubType = tumour_sample.tumourSubType
        migrated_tumour_sample.tumourType = tumour_sample.phase

        return self.validate_object(
            object_to_validate=migrated_tumour_sample, object_type=self.new_model.TumourSample
        )

    def migrate_tumour_samples(self, tumour_samples, LDPCode):
        return [self.migrate_tumour_sample(tumour_sample=tumour_sample, LDPCode=LDPCode) for tumour_sample in tumour_samples]

    def migrate_germline_sample(self, germline_sample, LDPCode):
        migrated_germline_sample = self.new_model.GermlineSample.fromJsonDict(germline_sample.toJsonDict())

        migrated_germline_sample.LDPCode = LDPCode

        return self.validate_object(
            object_to_validate=migrated_germline_sample, object_type=self.new_model.GermlineSample
        )

    def migrate_germline_samples(self, germline_samples, LDPCode):
        return [self.migrate_germline_sample(germline_sample=germline_sample, LDPCode=LDPCode) for germline_sample in germline_samples]

    def migrate_pedigree(self, old_pedigree):
        new_pedigree = self.new_model.Pedigree.fromJsonDict(old_pedigree.toJsonDict())
        new_pedigree.versionControl = self.new_model.VersionControl()

        new_pedigree.members = self.migrate_members(old_members=old_pedigree.members)

        if new_pedigree.validate(new_pedigree.toJsonDict()):
            return new_pedigree
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(new_pedigree.validate_parts())
            )

    def migrate_chiSquare1KGenomesPhase3Pop(self, old_chiSquare1KGenomesPhase3Pop):
        new_chiSquare1KGenomesPhase3Pop = self.new_model.ChiSquare1KGenomesPhase3Pop.fromJsonDict(old_chiSquare1KGenomesPhase3Pop.toJsonDict())
        new_chiSquare1KGenomesPhase3Pop.kgPopCategory = old_chiSquare1KGenomesPhase3Pop.kGPopCategory
        new_chiSquare1KGenomesPhase3Pop.kgSuperPopCategory = old_chiSquare1KGenomesPhase3Pop.kGSuperPopCategory

        if new_chiSquare1KGenomesPhase3Pop.validate(new_chiSquare1KGenomesPhase3Pop.toJsonDict()):
            return new_chiSquare1KGenomesPhase3Pop
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(new_chiSquare1KGenomesPhase3Pop.validate_parts())
            )

    def migrate_chiSquare1KGenomesPhase3Pops(self, old_chiSquare1KGenomesPhase3Pops):
        if old_chiSquare1KGenomesPhase3Pops is None:
            return None
        return [self.migrate_chiSquare1KGenomesPhase3Pop(old_chiSquare1KGenomesPhase3Pop) for old_chiSquare1KGenomesPhase3Pop in old_chiSquare1KGenomesPhase3Pops]

    def migrate_ancestries(self, old_ancestries):
        new_ancestries = self.new_model.Ancestries.fromJsonDict(old_ancestries.toJsonDict())
        new_ancestries.chiSquare1KGenomesPhase3Pop = self.migrate_chiSquare1KGenomesPhase3Pops(old_ancestries.chiSquare1KGenomesPhase3Pop)

        if new_ancestries.validate(new_ancestries.toJsonDict()):
            return new_ancestries
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(new_ancestries.validate_parts())
            )

    def migrate_member(self, old_member):
        new_member = self.new_model.PedigreeMember.fromJsonDict(old_member.toJsonDict())
        new_member.ancestries = self.migrate_ancestries(old_ancestries=old_member.ancestries)

        if new_member.validate(new_member.toJsonDict()):
            return new_member
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(new_member.validate_parts())
            )

    def migrate_members(self, old_members):
        return [self.migrate_member(old_member=old_member) for old_member in old_members]


class MigrationParticipants103To100(BaseMigration):
    old_model = participant_1_0_3
    new_model = participant_1_0_0

    def migrate_cancer_participant(self, cancer_participant):
        migrated_participant = self.new_model.CancerParticipant.fromJsonDict(cancer_participant.toJsonDict())

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

        migrated_participant.tumourSamples = self.migrate_tumour_samples(
            tumour_samples=cancer_participant.tumourSamples
        )

        migrated_participant.germlineSamples = self.migrate_germline_samples(
            germline_samples=cancer_participant.germlineSamples
        )

        migrated_participant.matchedSamples = self.migrate_matched_samples(
            matched_samples=cancer_participant.matchedSamples
        )

        return self.validate_object(
            object_to_validate=migrated_participant, object_type=self.new_model.CancerParticipant
        )

    def migrate_matched_samples(self, matched_samples):
        return [self.migrate_matched_sample(matched_sample=matched_sample) for matched_sample in matched_samples]

    def migrate_matched_sample(self, matched_sample):
        return self.new_model.MatchedSamples().fromJsonDict(matched_sample.toJsonDict())

    def migrate_germline_samples(self, germline_samples):
        return [self.migrate_germline_sample(germline_sample=germline_sample) for germline_sample in germline_samples]

    def migrate_germline_sample(self, germline_sample):
        return self.new_model.GermlineSample().fromJsonDict(germline_sample.toJsonDict())

    def migrate_tumour_samples(self, tumour_samples):
        return [self.migrate_tumour_sample(tumour_sample=tumour_sample) for tumour_sample in tumour_samples]

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


class MigrationReportsToParticipants1(BaseMigration):
    new_model = participant_1_0_0
    old_model = participant_old

    def migrate_pedigree(self, pedigree, ready_for_analysis=True):
        """

        :type pedigree: participant_old.Pedigree
        :rtype: participant_1_0_1.Pedigree
        """
        new_pedigree = self.new_model.Pedigree.fromJsonDict(pedigree.toJsonDict())
        new_pedigree.versionControl = self.new_model.VersionControl()
        new_pedigree.members = [self.migrate_pedigree_member(member=member) for member in pedigree.participants]
        analysis_panels = []
        if pedigree.analysisPanels is not None:
            for analysis_panel in pedigree.analysisPanels:
                analysis_panels.append(self.migrate_analysis_panel(analysis_panel=analysis_panel))
        new_pedigree.analysisPanels = analysis_panels
        new_pedigree.readyForAnalysis = ready_for_analysis
        new_pedigree.familyId = pedigree.gelFamilyId
        if new_pedigree.validate(new_pedigree.toJsonDict()):
            return new_pedigree
        else:
            raise Exception('This model can not be converted')

    @staticmethod
    def convert_to_float(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def migrate_disorder(self, disorder):
        new_disorder = self.new_model.Disorder().fromJsonDict(disorder.toJsonDict())
        new_disorder.ageOfOnset = self.convert_to_float(value=disorder.ageOfOnset)

        return self.validate_object(
            object_to_validate=new_disorder,
            object_type=self.new_model.Disorder
        )

    def migrate_pedigree_member(self, member, sample_id_to_lab_sample_id=None):
        """

        :type member: participant_old.RDParticipant
        :rtype: participant_1_0_1.PedigreeMember
        """
        new_pedigree_member = self.new_model.PedigreeMember.fromJsonDict(member.toJsonDict())
        new_pedigree_member.participantId = member.gelId
        new_pedigree_member.sex = self.migrate_enumerations('Sex', member.sex)
        new_pedigree_member.lifeStatus = self.migrate_enumerations('LifeStatus', member.lifeStatus)
        new_pedigree_member.adoptedStatus = self.migrate_enumerations('AdoptedStatus', member.adoptedStatus)
        new_pedigree_member.affectionStatus = self.migrate_enumerations('AffectionStatus', member.affectionStatus)
        new_pedigree_member.hpoTermList = [self.migrate_hpo_terms(hpo) for hpo in member.hpoTermList]
        new_pedigree_member.disorderList = [self.migrate_disorder(disorder) for disorder in member.disorderList]
        try:
            new_pedigree_member.yearOfBirth = int(member.yearOfBirth)
        except TypeError:
            new_pedigree_member.yearOfBirth = None

        new_pedigree_member.samples = []
        if member.samples is not None:
            for sample in member.samples:
                if sample_id_to_lab_sample_id is not None and isinstance(sample_id_to_lab_sample_id, dict):
                    try:
                        lab_sample_id = int(sample_id_to_lab_sample_id.get(sample, -1))
                    except ValueError:
                        lab_sample_id = -1
                else:
                    lab_sample_id = -1
                new_pedigree_member.samples.append(self.new_model.Sample(
                    sampleId=sample,
                    labSampleId=lab_sample_id
                ))
        if new_pedigree_member.validate(new_pedigree_member.toJsonDict()):
            return new_pedigree_member
        else:
            raise Exception('This model can not be converted')

    def migrate_enumerations(self, etype, value):
        if etype in ['LifeStatus', 'AffectionStatus']:
            if etype == 'AffectionStatus' and value == self.old_model.AffectionStatus.unknown:
                return self.new_model.AffectionStatus.UNCERTAIN
            else:
                return value.upper()
        elif etype == 'Sex':
            return {'male': 'MALE', 'female': 'FEMALE', 'unknown': 'UNKNOWN', 'undetermined': 'UNKNOWN'}.get(value)
        elif etype == 'AdoptedStatus':
            return {'not_adopted': 'notadopted', 'adoptedin': 'adoptedin', 'adoptedout': 'adoptedout'}.get(value)
        elif etype == 'termPresence':
            return {True: 'yes', False: 'no', None: 'unknown'}.get(value)
        else:
            raise NotImplementedError(etype + ' is not a valid enumeration type or is not implemented')

    def migrate_hpo_terms(self, hpo_term):
        """

        :type hpo_term: participant_old.HpoTerm
        :rtype: participant_1_0_1.HpoTerm
        """
        new_hpo = self.new_model.HpoTerm.fromJsonDict(hpo_term.toJsonDict())
        new_hpo.termPresence = self.migrate_enumerations('termPresence', hpo_term.termPresence)
        if new_hpo.validate(new_hpo.toJsonDict()):
            return new_hpo
        else:
            raise Exception('This model can not be converted')

    def migrate_analysis_panel(self, analysis_panel):
        """

        :type analysis_panel: participant_old.AnalysisPanel
        :rtype: participant_1_0_1.AnalysisPanel
        """

        new_analysis_panel = self.new_model.AnalysisPanel.fromJsonDict(analysis_panel.toJsonDict())
        new_analysis_panel.multipleGeneticOrigins = ''
        new_analysis_panel.reviewOutcome = ''
        if new_analysis_panel.validate(new_analysis_panel.toJsonDict()):
            return new_analysis_panel
        else:
            raise Exception('This model can not be converted')


class MigrationParticipants1ToReports(object):
    new_model = participant_old
    old_model = participant_1_0_0

    def migrate_pedigree(self, pedigree):
        """

        :type pedigree: participant_1_0_1.Pedigree
        :rtype: participant_old.Pedigree
        """
        new_pedigree = self.new_model.Pedigree.fromJsonDict(pedigree.toJsonDict())
        new_pedigree.versionControl = self.new_model.VersionControl()
        new_pedigree.analysisPanels = [self.migrate_analysis_panel(analysis_panel=panel) for panel in pedigree.analysisPanels]
        new_pedigree.gelFamilyId = pedigree.familyId
        new_pedigree.participants = [self.migrate_pedigree_member(member=member, family_id=new_pedigree.gelFamilyId) for member in pedigree.members]
        if new_pedigree.validate(new_pedigree.toJsonDict()):
            return new_pedigree
        else:
            raise Exception('This model can not be converted')

    def migrate_pedigree_member(self, member, family_id):
        """

        :type member: participant_1_0_1.PedigreeMember
        :rtype: participant_old.RDParticipant
        """
        new_pedigree_member = self.new_model.RDParticipant.fromJsonDict(member.toJsonDict())
        new_pedigree_member.versionControl = participant_old.VersionControl()
        new_pedigree_member.gelId = str(member.participantId)
        new_pedigree_member.gelFamilyId = family_id
        new_pedigree_member.sex = self.migrate_enumerations('Sex', member.sex)
        new_pedigree_member.lifeStatus = self.migrate_enumerations('LifeStatus', member.lifeStatus)
        new_pedigree_member.adoptedStatus = self.migrate_enumerations('AdoptedStatus', member.adoptedStatus)
        new_pedigree_member.affectionStatus = self.migrate_enumerations('AffectionStatus', member.affectionStatus)
        if new_pedigree_member.affectionStatus == 'uncertain':
            new_pedigree_member.affectionStatus = 'unknown'

        if member.hpoTermList:
            new_pedigree_member.hpoTermList = [self.migrate_hpo_terms(hpo) for hpo in member.hpoTermList]
        else:
            new_pedigree_member.hpoTermList = []
        try:
            new_pedigree_member.yearOfBirth = str(int(member.yearOfBirth))
        except TypeError:
            new_pedigree_member.yearOfBirth = None

        if member.samples:
            new_pedigree_member.samples = [sample.sampleId for sample in member.samples]
        else:
            new_pedigree_member.samples = []

        if member.disorderList:
            new_pedigree_member.disorderList = [self.migrate_disorders(d) for d in member.disorderList]
        else:
            new_pedigree_member.disorderList = []

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
        new_hpo = self.new_model.HpoTerm.fromJsonDict(hpo_term.toJsonDict())
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
        new_disorder = self.new_model.Disorder.fromJsonDict(disorder.toJsonDict())
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

        new_analysis_panel = self.new_model.AnalysisPanel.fromJsonDict(analysis_panel.toJsonDict())
        new_analysis_panel.multiple_genetic_origins = analysis_panel.multipleGeneticOrigins
        new_analysis_panel.review_outcome = analysis_panel.reviewOutcome
        if new_analysis_panel.validate(new_analysis_panel.toJsonDict()):
            return new_analysis_panel
        else:
            raise Exception('This model can not be converted')

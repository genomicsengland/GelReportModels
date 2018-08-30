import logging

from past.builtins import basestring

from protocols import participant_1_0_0
from protocols import reports_3_0_0
from protocols.util import handle_avro_errors
from protocols.migration.base_migration import BaseMigration, MigrationError


class MigrationReports3ToParticipant1(BaseMigration):
    """
    Any participant with empty labId in tumour or germline sample will fail to validate.
    """
    old_model = reports_3_0_0
    new_model = participant_1_0_0

    def migrate_pedigree(self, pedigree, ready_for_analysis=True):
        """

        :type pedigree: participant_old.Pedigree
        :rtype: participant_1_0_1.Pedigree
        """
        new_pedigree = self.convert_class(self.new_model.Pedigree, pedigree)
        new_pedigree.versionControl = self.new_model.VersionControl()
        new_pedigree.members = self.convert_collection(pedigree.participants, self.migrate_pedigree_member)
        new_pedigree.analysisPanels = self.convert_collection(
            pedigree.analysisPanels, self.migrate_analysis_panel, default=[])
        new_pedigree.readyForAnalysis = ready_for_analysis
        new_pedigree.familyId = pedigree.gelFamilyId
        if new_pedigree.validate(new_pedigree.toJsonDict()):
            return new_pedigree
        else:
            raise MigrationError('This model can not be converted')

    def migrate_pedigree_member(self, member, sample_id_to_lab_sample_id=None):
        """

        :type member: participant_old.RDParticipant
        :rtype: participant_1_0_1.PedigreeMember
        """
        new_pedigree_member = self.convert_class(self.new_model.PedigreeMember, member)
        new_pedigree_member.participantId = member.gelId
        new_pedigree_member.sex = self.migrate_enumerations('Sex', member.sex)
        new_pedigree_member.lifeStatus = self.migrate_enumerations('LifeStatus', member.lifeStatus)
        new_pedigree_member.adoptedStatus = self.migrate_enumerations('AdoptedStatus', member.adoptedStatus)
        new_pedigree_member.affectionStatus = self.migrate_enumerations('AffectionStatus', member.affectionStatus)
        new_pedigree_member.hpoTermList = self.convert_collection(member.hpoTermList, self.migrate_hpo_terms)
        try:
            new_pedigree_member.yearOfBirth = self.convert_string_to_integer(member.yearOfBirth)
        except MigrationError:
            new_pedigree_member.yearOfBirth = None
            logging.warning("We are losing the year of birth as it cannot be converted into an integer")

        new_pedigree_member.samples = []
        if member.samples is not None:
            for sample in member.samples:
                if sample_id_to_lab_sample_id is not None and isinstance(sample_id_to_lab_sample_id, dict):
                    lab_sample_id = self.convert_string_to_integer(
                        sample_id_to_lab_sample_id.get(sample, -1), default_value=-1)
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
        new_hpo = self.convert_class(self.new_model.HpoTerm, hpo_term)
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

        new_analysis_panel = self.convert_class(self.new_model.AnalysisPanel, analysis_panel)
        new_analysis_panel.multipleGeneticOrigins = ''
        new_analysis_panel.reviewOutcome = ''
        if new_analysis_panel.validate(new_analysis_panel.toJsonDict()):
            return new_analysis_panel
        else:
            raise Exception('This model can not be converted')

    def migrate_cancer_participant(self, old_cancer_participant):
        """
        PRE: germlineSamples.labId follows an integer format
        :type old_cancer_participant: reports_3_0_0.CancerParticipant
        :rtype: participant_1_0_0.CancerParticipant
        """
        new_cancer_participant = self.convert_class(self.new_model.CancerParticipant, old_cancer_participant)

        new_cancer_participant.versionControl.GitVersionControl = '1.0.0'
        new_cancer_participant.additionalInformation = old_cancer_participant.cancerDemographics.additionalInformation
        new_cancer_participant.assignedICD10 = old_cancer_participant.cancerDemographics.assignedICD10
        new_cancer_participant.center = old_cancer_participant.cancerDemographics.center
        new_cancer_participant.LDPCode = old_cancer_participant.cancerDemographics.center
        new_cancer_participant.consentStatus = old_cancer_participant.cancerDemographics.consentStatus
        new_cancer_participant.sex = self.migrate_sex(old_sex=old_cancer_participant.cancerDemographics.sex)
        new_cancer_participant.individualId = old_cancer_participant.cancerDemographics.gelId
        new_cancer_participant.primaryDiagnosisDisease = old_cancer_participant.cancerDemographics.primaryDiagnosis
        new_cancer_participant.readyForAnalysis = True

        if old_cancer_participant.cancerSamples is not None:
            germline_samples = list(
                filter(
                    lambda s: s.sampleType == self.old_model.SampleType.germline, old_cancer_participant.cancerSamples
                )
            )
            new_cancer_participant.germlineSamples = self.convert_collection(
                things=germline_samples, migrate_function=self.migrate_germline_sample
            )

        if old_cancer_participant.cancerSamples is not None:
            tumor_samples = list(filter(lambda s: s.sampleType == self.old_model.SampleType.tumor,
                                   old_cancer_participant.cancerSamples))
            new_cancer_participant.tumourSamples = self.convert_collection(
                things=tumor_samples, migrate_function=self.migrate_tumor_sample
            )

        new_cancer_participant.matchedSamples = self.convert_collection(
            old_cancer_participant.matchedSamples, self.migrate_match_samples)

        return self.validate_object(
            object_to_validate=new_cancer_participant, object_type=self.new_model.CancerParticipant
        )

    def migrate_tumor_sample(self, old_cancer_sample):

        new_tumour_sample = self.convert_class(self.new_model.TumourSample, old_cancer_sample)

        new_tumour_sample.TNMStageGrouping = old_cancer_sample.tmn_stage_grouping
        new_tumour_sample.TNMStageVersion = old_cancer_sample.tmn_stage_grouping
        try:
            new_tumour_sample.labSampleId = self.convert_string_to_integer(string=old_cancer_sample.labId)
        except MigrationError as ex:
            logging.error("Laboratory identifier in tumour sample cannot be converted to an integer!")
            raise ex
        new_tumour_sample.programmePhase = old_cancer_sample.gelPhase

        new_tumour_sample.preparationMethod = old_cancer_sample.preservationMethod
        new_tumour_sample.source = participant_1_0_0.SampleSource.TUMOUR

        new_tumour_type = None
        if isinstance(old_cancer_sample.tumorType, basestring):
            old_tumour_type = old_cancer_sample.tumorType.upper()
            new_tumour_type = getattr(participant_1_0_0.TumourType, old_tumour_type, None)
        new_tumour_sample.tumourType = new_tumour_type

        new_tumour_content = None
        if isinstance(old_cancer_sample.tumorContent, basestring):
            old_tumor_content = old_cancer_sample.tumorContent
            new_tumour_content = getattr(participant_1_0_0.TumourContent, old_tumor_content.title(), None)
        new_tumour_sample.tumourContent = new_tumour_content

        new_tumour_sample.tumourSubType = old_cancer_sample.tumorSubType

        new_tumour_sample.tumourId = 1

        phase_map = {
            reports_3_0_0.Phase.PRIMARY: participant_1_0_0.Phase.PRIMARY,
            reports_3_0_0.Phase.METASTATIC: participant_1_0_0.Phase.METASTASES,
            reports_3_0_0.Phase.RECURRENCE: participant_1_0_0.Phase.RECURRENCE_OF_PRIMARY_TUMOUR
        }
        new_tumour_sample.phase = phase_map.get(old_cancer_sample.phase)

        preservation_to_preparation_map = {
            reports_3_0_0.PreservationMethod.BLOOD: participant_1_0_0.PreparationMethod.EDTA,
            reports_3_0_0.PreservationMethod.SALIVA: participant_1_0_0.PreparationMethod.ORAGENE,
            reports_3_0_0.PreservationMethod.UNKNOWN: None,
            reports_3_0_0.PreservationMethod.GL: None,
            reports_3_0_0.PreservationMethod.LEUK: None,
        }
        new_tumour_sample.preparationMethod = preservation_to_preparation_map.get(
            old_cancer_sample.preservationMethod)

        return self.validate_object(
            object_to_validate=new_tumour_sample, object_type=self.new_model.TumourSample
        )

    def migrate_match_samples(self, old_match_samples):
        new_match_sample = self.convert_class(self.new_model.MatchedSamples, old_match_samples)
        new_match_sample.tumourSampleId = old_match_samples.tumorSampleId
        return new_match_sample

    def migrate_germline_sample(self, old_cancer_sample):

        new_germline_sample = self.convert_class(self.new_model.GermlineSample, old_cancer_sample)

        try:
            new_germline_sample.labSampleId = self.convert_string_to_integer(string=old_cancer_sample.labId)
        except MigrationError as ex:
            logging.error("Laboratory identifier in germline sample cannot be converted to an integer!")
            raise ex

        preservation_to_preparation_map = {
            reports_3_0_0.PreservationMethod.BLOOD: participant_1_0_0.PreparationMethod.EDTA,
            reports_3_0_0.PreservationMethod.SALIVA: participant_1_0_0.PreparationMethod.ORAGENE,
            reports_3_0_0.PreservationMethod.UNKNOWN: None,
            reports_3_0_0.PreservationMethod.GL: None,
            reports_3_0_0.PreservationMethod.LEUK: None,
        }
        new_germline_sample.preparationMethod = preservation_to_preparation_map.get(
            old_cancer_sample.preservationMethod)

        preservation_to_source_map = {
            reports_3_0_0.PreservationMethod.BLOOD: participant_1_0_0.SampleSource.BLOOD,
            reports_3_0_0.PreservationMethod.SALIVA: participant_1_0_0.SampleSource.SALIVA,
            reports_3_0_0.PreservationMethod.FF: participant_1_0_0.SampleSource.TUMOUR,
            reports_3_0_0.PreservationMethod.FFPE: participant_1_0_0.SampleSource.TUMOUR,
            reports_3_0_0.PreservationMethod.UNKNOWN: None,
            reports_3_0_0.PreservationMethod.GL: None,
            reports_3_0_0.PreservationMethod.LEUK: None,
        }
        new_germline_sample.source = preservation_to_source_map.get(
            old_cancer_sample.preservationMethod)

        new_germline_sample.programmePhase = old_cancer_sample.gelPhase

        if new_germline_sample.validate(new_germline_sample.toJsonDict(), verbose=True):
            return new_germline_sample
        else:
            # TODO(Greg): Improve these error messages
            raise Exception('This model can not be converted: ', new_germline_sample.validate_parts())

    def migrate_sex(self, old_sex):
        sex_map = {
            'F': self.new_model.Sex.FEMALE,
            'M': self.new_model.Sex.MALE
        }
        return sex_map.get(old_sex, self.new_model.Sex.UNKNOWN)

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

    def migrate_pedigree(self, pedigree, ready_for_analysis=True, ldp_code=None):
        """
        :type ready_for_analysis: bool
        :type pedigree: participant_old.Pedigree
        :type ldp_code: str
        :rtype: participant_1_0_1.Pedigree
        """
        new_instance = self.convert_class(self.new_model.Pedigree, pedigree)
        new_instance.versionControl = self.new_model.VersionControl()
        new_instance.members = self.convert_collection(pedigree.participants, self._migrate_pedigree_member)
        new_instance.readyForAnalysis = ready_for_analysis
        new_instance.familyId = pedigree.gelFamilyId
        if ldp_code:
            new_instance.LDPCode = ldp_code
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Pedigree)

    def migrate_cancer_participant(self, old_cancer_participant):
        """
        PRE: germlineSamples.labId follows an integer format
        :type old_cancer_participant: reports_3_0_0.CancerParticipant
        :rtype: participant_1_0_0.CancerParticipant
        """
        new_instance = self.convert_class(self.new_model.CancerParticipant, old_cancer_participant)

        new_instance.versionControl.GitVersionControl = '1.0.0'
        new_instance.additionalInformation = old_cancer_participant.cancerDemographics.additionalInformation
        new_instance.assignedICD10 = old_cancer_participant.cancerDemographics.assignedICD10
        new_instance.center = old_cancer_participant.cancerDemographics.center
        new_instance.LDPCode = old_cancer_participant.cancerDemographics.center
        new_instance.consentStatus = old_cancer_participant.cancerDemographics.consentStatus
        new_instance.sex = self._migrate_sex(old_sex=old_cancer_participant.cancerDemographics.sex)
        new_instance.individualId = old_cancer_participant.cancerDemographics.gelId
        new_instance.primaryDiagnosisDisease = old_cancer_participant.cancerDemographics.primaryDiagnosis
        new_instance.readyForAnalysis = True
        if old_cancer_participant.cancerSamples is not None:
            germline_samples = list(
                filter(
                    lambda s: s.sampleType == self.old_model.SampleType.germline, old_cancer_participant.cancerSamples
                )
            )
            new_instance.germlineSamples = self.convert_collection(
                things=germline_samples, migrate_function=self._migrate_germline_sample
            )
        if old_cancer_participant.cancerSamples is not None:
            tumor_samples = list(filter(lambda s: s.sampleType == self.old_model.SampleType.tumor,
                                        old_cancer_participant.cancerSamples))
            new_instance.tumourSamples = self.convert_collection(
                things=tumor_samples, migrate_function=self._migrate_tumor_sample
            )
        new_instance.matchedSamples = self.convert_collection(
            old_cancer_participant.matchedSamples, self._migrate_match_samples)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.CancerParticipant)

    def _migrate_pedigree_member(self, member, sample_id_to_lab_sample_id=None):
        new_instance = self.convert_class(self.new_model.PedigreeMember, member)
        new_instance.participantId = member.gelId
        new_instance.sex = self._migrate_enumerations('Sex', member.sex)
        new_instance.lifeStatus = self._migrate_enumerations('LifeStatus', member.lifeStatus)
        new_instance.adoptedStatus = self._migrate_enumerations('AdoptedStatus', member.adoptedStatus)
        new_instance.affectionStatus = self._migrate_enumerations('AffectionStatus', member.affectionStatus)
        new_instance.personKaryotypicSex = self._migrate_enumerations('PersonKaryotipicSex', member.personKaryotipicSex)
        new_instance.hpoTermList = self.convert_collection(member.hpoTermList, self._migrate_hpo_terms)
        new_instance.yearOfBirth = self.convert_string_to_integer(
            member.yearOfBirth, default_value=None, fail=False,
            defaulting_message="We are losing the year of birth as it cannot be converted into an integer")

        new_instance.samples = []
        if member.samples is not None:
            for sample in member.samples:
                if sample_id_to_lab_sample_id is not None and isinstance(sample_id_to_lab_sample_id, dict):
                    lab_sample_id = self.convert_string_to_integer(
                        sample_id_to_lab_sample_id.get(sample, -1), default_value=-1)
                else:
                    lab_sample_id = -1
                new_instance.samples.append(self.new_model.Sample(
                    sampleId=sample,
                    labSampleId=lab_sample_id
                ))
        return new_instance

    def _migrate_enumerations(self, etype, value):
        # TODO: use enums and avoid hard coding strings
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
        elif etype == 'PersonKaryotipicSex':
            return {'unknown': 'UNKNOWN', 'XX': 'XX', 'XY': 'XY', 'XO': 'XO', 'XXY': 'XXY', 'XXX': 'XXX',
                    'XXYY': 'XXYY', 'XXXY': 'XXXY', 'XXXX': 'XXXX', 'XYY': 'XYY', 'other':'OTHER'}.get(value)
        else:
            raise NotImplementedError(etype + ' is not a valid enumeration type or is not implemented')

    def _migrate_hpo_terms(self, hpo_term):
        """

        :type hpo_term: participant_old.HpoTerm
        :rtype: participant_1_0_1.HpoTerm
        """
        new_instance = self.convert_class(self.new_model.HpoTerm, hpo_term)
        new_instance.termPresence = self._migrate_enumerations('termPresence', hpo_term.termPresence)
        return new_instance

    def _migrate_tumor_sample(self, old_cancer_sample):

        new_instance = self.convert_class(self.new_model.TumourSample, old_cancer_sample)

        new_instance.TNMStageGrouping = old_cancer_sample.tmn_stage_grouping
        new_instance.TNMStageVersion = old_cancer_sample.tmn_stage_grouping
        try:
            new_instance.labSampleId = self.convert_string_to_integer(string=old_cancer_sample.labId)
        except MigrationError as ex:
            logging.error("Laboratory identifier in tumour sample cannot be converted to an integer!")
            raise ex
        new_instance.programmePhase = old_cancer_sample.gelPhase

        new_instance.preparationMethod = old_cancer_sample.preservationMethod
        new_instance.source = participant_1_0_0.SampleSource.TUMOUR

        new_tumour_type = None
        if isinstance(old_cancer_sample.tumorType, basestring):
            old_tumour_type = old_cancer_sample.tumorType.upper()
            new_tumour_type = getattr(participant_1_0_0.TumourType, old_tumour_type, None)
        new_instance.tumourType = new_tumour_type

        new_tumour_content = None
        if isinstance(old_cancer_sample.tumorContent, basestring):
            old_tumor_content = old_cancer_sample.tumorContent
            new_tumour_content = getattr(participant_1_0_0.TumourContent, old_tumor_content.title(), None)
        new_instance.tumourContent = new_tumour_content

        new_instance.tumourSubType = old_cancer_sample.tumorSubType

        new_instance.tumourId = 1

        phase_map = {
            reports_3_0_0.Phase.PRIMARY: participant_1_0_0.Phase.PRIMARY,
            reports_3_0_0.Phase.METASTATIC: participant_1_0_0.Phase.METASTASES,
            reports_3_0_0.Phase.RECURRENCE: participant_1_0_0.Phase.RECURRENCE_OF_PRIMARY_TUMOUR
        }
        new_instance.phase = phase_map.get(old_cancer_sample.phase)

        preservation_to_preparation_map = {
            reports_3_0_0.PreservationMethod.BLOOD: participant_1_0_0.PreparationMethod.EDTA,
            reports_3_0_0.PreservationMethod.SALIVA: participant_1_0_0.PreparationMethod.ORAGENE,
            reports_3_0_0.PreservationMethod.UNKNOWN: None,
            reports_3_0_0.PreservationMethod.GL: None,
            reports_3_0_0.PreservationMethod.LEUK: None,
        }
        new_instance.preparationMethod = preservation_to_preparation_map.get(
            old_cancer_sample.preservationMethod)
        return new_instance

    def _migrate_match_samples(self, old_match_samples):
        new_match_sample = self.convert_class(self.new_model.MatchedSamples, old_match_samples)
        new_match_sample.tumourSampleId = old_match_samples.tumorSampleId
        return new_match_sample

    def _migrate_germline_sample(self, old_cancer_sample):

        new_instance = self.convert_class(self.new_model.GermlineSample, old_cancer_sample)
        new_instance.labSampleId = self.convert_string_to_integer(string=old_cancer_sample.labId)
        preservation_to_preparation_map = {
            reports_3_0_0.PreservationMethod.BLOOD: participant_1_0_0.PreparationMethod.EDTA,
            reports_3_0_0.PreservationMethod.SALIVA: participant_1_0_0.PreparationMethod.ORAGENE,
            reports_3_0_0.PreservationMethod.UNKNOWN: None,
            reports_3_0_0.PreservationMethod.GL: None,
            reports_3_0_0.PreservationMethod.LEUK: None,
        }
        new_instance.preparationMethod = preservation_to_preparation_map.get(
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
        new_instance.source = preservation_to_source_map.get(
            old_cancer_sample.preservationMethod)
        new_instance.programmePhase = old_cancer_sample.gelPhase
        return new_instance

    def _migrate_sex(self, old_sex):
        sex_map = {
            'F': self.new_model.Sex.FEMALE,
            'M': self.new_model.Sex.MALE
        }
        return sex_map.get(old_sex, self.new_model.Sex.UNKNOWN)

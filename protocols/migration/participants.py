import logging
from protocols import reports_3_0_0 as participant_old
from protocols import participant_1_0_0
from protocols import participant_1_0_1
from protocols import participant_1_0_3
from protocols import participant_1_1_0
from protocols.util import handle_avro_errors
from protocols.migration import BaseMigration
from protocols.migration.base_migration import MigrationError


class MigrationParticipants103To110(BaseMigration):
    old_model = participant_1_0_3
    new_model = participant_1_1_0

    def migrate_pedigree(self, old_instance):
        new_instance = self.convert_class(self.new_model.Pedigree, old_instance)
        if new_instance.validate(new_instance.toJsonDict()):
            return new_instance
        else:
            raise MigrationError(
                'This model can not be converted: ', handle_avro_errors(new_instance.validate_parts())
            )

    def migrate_cancer_participant(self, old_instance):
        """

        :param old_instance:
        :type old_instance: participants_1_0_3.CancerParticipant
        :return:
        """
        new_instance = self.convert_class(self.new_model.CancerParticipant, old_instance)   # type: participant_1_1_0.CancerParticipant

        if old_instance.tumourSamples is not None:
            new_instance.tumourSamples = [self._migrate_tumour_sample(tumour_sample)
                                          for tumour_sample in old_instance.tumourSamples]

        if new_instance.validate(new_instance.toJsonDict()):
            return new_instance
        else:
            raise MigrationError(
                'This model can not be converted: ', handle_avro_errors(new_instance.validate_parts())
            )

    def _migrate_tumour_sample(self, old_instance):
        """

        :param old_instance:
        :type old_instance: old_model.TumourSample
        :return:
        """
        new_instance = self.convert_class(self.new_model.TumourSample, old_instance)  # type: new_model.TumourSample

        if old_instance.morphologyICD is not None:
            new_instance.morphologyICDs = [old_instance.morphologyICD]
        if old_instance.morphologySnomedCT is not None:
            new_instance.morphologySnomedCTs = [old_instance.morphologySnomedCT]
        if old_instance.morphologySnomedRT is not None:
            new_instance.morphologySnomedRTs = [old_instance.morphologySnomedRT]
        if old_instance.topographyICD is not None:
            new_instance.topographyICDs = [old_instance.topographyICD]
        if old_instance.topographySnomedCT is not None:
            new_instance.topographySnomedCTs = [old_instance.topographySnomedCT]
        if old_instance.topographySnomedRT is not None:
            new_instance.topographySnomedRTs = [old_instance.topographySnomedRT]

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.TumourSample
        )


class MigrationParticipants110To100(BaseMigration):
    old_model = participant_1_1_0
    new_model = participant_1_0_0

    def migrate_pedigree(self, old_instance):
        new_instance = self.convert_class(self.new_model.Pedigree, old_instance)
        new_instance.versionControl = self.new_model.VersionControl()
        new_instance.members = [self.migrate_member(member) for member in old_instance.members]
        if new_instance.validate(new_instance.toJsonDict()):
            return new_instance
        else:
            raise MigrationError(
                'This model can not be converted: ', handle_avro_errors(new_instance.validate_parts())
            )

    def migrate_member(self, old_instance):
        new_instance = self.convert_class(self.new_model.PedigreeMember, old_instance)
        if old_instance.hpoTermList is not None:
            new_instance.hpoTermList = [self.migrate_hpo(hpo) for hpo in old_instance.hpoTermList]
        if old_instance.disorderList is not None:
            new_instance.disorderList = [self.migrate_disorder(disorder) for disorder in old_instance.disorderList]
        if old_instance.ancestries is not None:
            new_instance.ancestries = self.migrate_ancestries(old_instance.ancestries)
        if old_instance.samples is not None:
            new_instance.samples= [self.migrate_sample(sample) for sample in old_instance.samples]
        return new_instance

    def migrate_hpo(self, old_instance):
        new_instance = self.convert_class(self.new_model.HpoTerm, old_instance)
        new_instance.modifiers = {}
        if old_instance.modifiers.laterality is not None:
            new_instance.modifiers['laterality'] = old_instance.modifiers.laterality
        if old_instance.modifiers.progression is not None:
            new_instance.modifiers['progression'] = old_instance.modifiers.progression
        if old_instance.modifiers.severity is not None:
            new_instance.modifiers['severity'] = old_instance.modifiers.severity
        if old_instance.modifiers.spatialPattern is not None:
            new_instance.modifiers['spatialPattern'] = old_instance.modifiers.spatialPattern
        return new_instance

    def migrate_disorder(self, old_instance):
        new_instance = self.convert_class(self.new_model.Disorder, old_instance)
        new_instance.ageOfOnset = str(old_instance.ageOfOnset)
        return new_instance

    def migrate_ancestries(self, old_instance):
        new_instance = self.convert_class(self.new_model.Ancestries, old_instance)
        if old_instance.chiSquare1KGenomesPhase3Pop is not None:
            new_instance.chiSquare1KGenomesPhase3Pop = [self.migrate_chi(chi)
                                                        for chi in old_instance.chiSquare1KGenomesPhase3Pop]
        return new_instance

    def migrate_chi(self, old_instance):
        new_instance = self.convert_class(self.new_model.ChiSquare1KGenomesPhase3Pop, old_instance)
        new_instance.kGSuperPopCategory = old_instance.kgSuperPopCategory
        new_instance.kGPopCategory = old_instance.kgPopCategory
        return new_instance

    def migrate_sample(self, old_instance):
        new_instance = self.convert_class(self.new_model.Sample, old_instance)
        valid_sources = [self.new_model.RDSampleSource.SALIVA, self.new_model.RDSampleSource.BLOOD,
                         self.new_model.RDSampleSource.FIBROBLAST, self.new_model.RDSampleSource.TISSUE]
        if new_instance.source not in valid_sources:
            new_instance.source = None
        return new_instance


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
        return self.convert_class(self.new_model.MatchedSamples(), matched_sample)

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

    def migrate_tumour_samples(self, tumour_samples, LDPCode):
        if tumour_samples is not None:
            return [self.migrate_tumour_sample(tumour_sample=tumour_sample, LDPCode=LDPCode) for tumour_sample in tumour_samples]
        return None

    def migrate_germline_sample(self, germline_sample, LDPCode):
        migrated_germline_sample = self.convert_class(self.new_model.GermlineSample, germline_sample)

        migrated_germline_sample.LDPCode = LDPCode

        return self.validate_object(
            object_to_validate=migrated_germline_sample, object_type=self.new_model.GermlineSample
        )

    def migrate_germline_samples(self, germline_samples, LDPCode):
        if germline_samples is not None:
            return [self.migrate_germline_sample(germline_sample=germline_sample, LDPCode=LDPCode) for germline_sample in germline_samples]
        return None

    def migrate_pedigree(self, old_pedigree):
        new_pedigree = self.convert_class(self.new_model.Pedigree, old_pedigree)
        new_pedigree.versionControl = self.new_model.VersionControl()

        new_pedigree.members = self.migrate_members(old_members=old_pedigree.members)

        if new_pedigree.validate(new_pedigree.toJsonDict()):
            return new_pedigree
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(new_pedigree.validate_parts())
            )

    def migrate_chiSquare1KGenomesPhase3Pop(self, old_chiSquare1KGenomesPhase3Pop):
        new_chiSquare1KGenomesPhase3Pop = self.new_model.ChiSquare1KGenomesPhase3Pop.fromJsonDict(
            old_chiSquare1KGenomesPhase3Pop.toJsonDict())
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
        new_ancestries = self.convert_class(self.new_model.Ancestries, old_ancestries)
        new_ancestries.chiSquare1KGenomesPhase3Pop = self.migrate_chiSquare1KGenomesPhase3Pops(old_ancestries.chiSquare1KGenomesPhase3Pop)

        if new_ancestries.validate(new_ancestries.toJsonDict()):
            return new_ancestries
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(new_ancestries.validate_parts())
            )

    def migrate_member(self, old_member):
        new_member = self.convert_class(self.new_model.PedigreeMember, old_member)
        new_member.ancestries = self.migrate_ancestries(old_ancestries=old_member.ancestries)
        if old_member.disorderList is not None:
            new_member.disorderList = [self.migrate_disorder(disorder) for disorder in old_member.disorderList]
        if old_member.hpoTermList is not None:
            new_member.hpoTermList = [self.migrate_hpo_term(hpo_term) for hpo_term in old_member.hpoTermList]
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

    def migrate_members(self, old_members):
        if old_members is not None:
            return [self.migrate_member(old_member=old_member) for old_member in old_members]
        return None


class MigrationReportsToParticipants1(BaseMigration):
    old_model = participant_old
    new_model = participant_1_0_0

    def migrate_pedigree(self, pedigree, ready_for_analysis=True):
        """

        :type pedigree: participant_old.Pedigree
        :rtype: participant_1_0_1.Pedigree
        """
        new_pedigree = self.convert_class(self.new_model.Pedigree, pedigree)
        new_pedigree.versionControl = self.new_model.VersionControl()
        if pedigree.participants is not None:
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
            raise MigrationError('This model can not be converted')

    def migrate_disorder(self, disorder):
        new_disorder = self.convert_class(self.new_model.Disorder(), disorder)

        return self.validate_object(
            object_to_validate=new_disorder,
            object_type=self.new_model.Disorder
        )

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
        if member.hpoTermList is not None:
            new_pedigree_member.hpoTermList = [self.migrate_hpo_terms(hpo) for hpo in member.hpoTermList]
        if member.disorderList is not None:
            new_pedigree_member.disorderList = [self.migrate_disorder(disorder) for disorder in member.disorderList]
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


class MigrationParticipants101ToReports(object):
    old_model = participant_1_0_1
    new_model = participant_old

    def migrate_pedigree(self, pedigree):
        """

        :type pedigree: participant_1_0_1.Pedigree
        :rtype: participant_old.Pedigree
        """
        new_pedigree = self.convert_class(self.new_model.Pedigree, pedigree)
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
        return self.convert_class(self.new_model.MatchedSamples(), matched_sample)

    def migrate_germline_samples(self, germline_samples):
        if germline_samples is not None:
            return [self.migrate_germline_sample(germline_sample=germline_sample) for germline_sample in germline_samples]
        return None

    def migrate_germline_sample(self, germline_sample):
        return self.convert_class(self.new_model.GermlineSample(), germline_sample)

    def migrate_tumour_samples(self, tumour_samples):
        if tumour_samples is not None:
            return [self.migrate_tumour_sample(tumour_sample=tumour_sample) for tumour_sample in tumour_samples]
        return None

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
        new_pedigree.analysisPanels = self.migrate_analysis_panels(old_panels=old_pedigree.analysisPanels)
        new_pedigree.participants = self.migrate_members_to_participants(old_members=old_pedigree.members,
                                                                         family_id=old_pedigree.familyId)
        return self.validate_object(object_to_validate=new_pedigree, object_type=self.new_model.Pedigree)

    def migrate_members_to_participants(self, old_members, family_id):
        return [self.migrate_member_to_participant(old_member=old_member, family_id=family_id) for old_member in
                old_members]

    def migrate_member_to_participant(self, old_member, family_id):
        new_participant = self.convert_class(self.new_model.RDParticipant, old_member)
        new_participant.gelFamilyId = family_id
        new_participant.pedigreeId = old_member.pedigreeId or 0
        new_participant.isProband = old_member.isProband or False
        new_participant.sex = self.migrate_sex(old_sex=old_member.sex)
        new_participant.personKaryotipicSex = self.migrate_person_karyotypic_sex(old_pks=old_member.personKaryotypicSex)
        new_participant.yearOfBirth = str(old_member.yearOfBirth)
        new_participant.adoptedStatus = self.migrate_adopted_status(old_status=old_member.adoptedStatus)
        new_participant.lifeStatus = self.migrate_life_status(old_status=old_member.lifeStatus)
        new_participant.affectionStatus = self.migrate_affection_status(old_status=old_member.affectionStatus)
        new_participant.hpoTermList = self.migrate_hpo_term_list(old_list=old_member.hpoTermList)
        new_participant.samples = self.migrate_samples(old_samples=old_member.samples)
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

    @staticmethod
    def migrate_samples(old_samples):
        return None if old_samples is None else [old_sample.sampleId for old_sample in old_samples]

    def migrate_hpo_term_list(self, old_list):
        return [] if old_list is None else [self.migrate_hpo_term(old_term=old_term) for old_term in old_list]

    def migrate_hpo_term(self, old_term):
        new_term = self.convert_class(target_klass=self.new_model.HpoTerm, instance=old_term)
        new_term.termPresence = self.migrate_ternary_option_to_boolean(ternary_option=old_term.termPresence)
        return self.validate_object(object_to_validate=new_term, object_type=self.new_model.HpoTerm)

    def migrate_ternary_option_to_boolean(self, ternary_option):
        ternary_map = {
            self.old_model.TernaryOption.no: False,
            self.old_model.TernaryOption.yes: True,
        }
        return ternary_map.get(ternary_option, False)

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

    def migrate_analysis_panels(self, old_panels):
        return None if old_panels is None else [self.migrate_analysis_panel(old_panel=old_panel) for old_panel in
                                                old_panels]

    def migrate_analysis_panel(self, old_panel):
        new_panel = self.convert_class(self.new_model.AnalysisPanel, old_panel)
        new_panel.review_outcome = old_panel.reviewOutcome
        new_panel.multiple_genetic_origins = old_panel.multipleGeneticOrigins
        return self.validate_object(object_to_validate=new_panel, object_type=self.new_model.AnalysisPanel)


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
        new_pedigree.analysisPanels = self.migrate_analysis_panels(old_panels=old_pedigree.analysisPanels)
        new_pedigree.participants = self.migrate_members_to_participants(
            old_members=old_pedigree.members, family_id=old_pedigree.familyId)
        return self.validate_object(object_to_validate=new_pedigree, object_type=self.new_model.Pedigree)

    def migrate_members_to_participants(self, old_members, family_id):
        return [self.migrate_member_to_participant(old_member=old_member, family_id=family_id)
                for old_member in old_members]

    def migrate_member_to_participant(self, old_member, family_id):
        new_participant = self.convert_class(self.new_model.RDParticipant, old_member)
        new_participant.gelFamilyId = family_id
        new_participant.pedigreeId = old_member.pedigreeId or 0
        new_participant.isProband = old_member.isProband or False
        new_participant.sex = self.migrate_sex(old_sex=old_member.sex)
        new_participant.personKaryotipicSex = self.migrate_person_karyotypic_sex(old_pks=old_member.personKaryotypicSex)
        new_participant.yearOfBirth = str(old_member.yearOfBirth)
        new_participant.adoptedStatus = self.migrate_adopted_status(old_status=old_member.adoptedStatus)
        new_participant.lifeStatus = self.migrate_life_status(old_status=old_member.lifeStatus)
        new_participant.affectionStatus = self.migrate_affection_status(old_status=old_member.affectionStatus)
        new_participant.hpoTermList = self.migrate_hpo_term_list(old_list=old_member.hpoTermList)
        new_participant.samples = self.migrate_samples(old_samples=old_member.samples)
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

    @staticmethod
    def migrate_samples(old_samples):
        return None if old_samples is None else [old_sample.sampleId for old_sample in old_samples]

    def migrate_hpo_term_list(self, old_list):
        return [] if old_list is None else [self.migrate_hpo_term(old_term=old_term) for old_term in old_list]

    def migrate_hpo_term(self, old_term):
        new_term = self.convert_class(target_klass=self.new_model.HpoTerm, instance=old_term)
        new_term.termPresence = self.migrate_ternary_option_to_boolean(ternary_option=old_term.termPresence)
        return self.validate_object(object_to_validate=new_term, object_type=self.new_model.HpoTerm)

    def migrate_ternary_option_to_boolean(self, ternary_option):
        ternary_map = {
            self.old_model.TernaryOption.no: False,
            self.old_model.TernaryOption.yes: True,
        }
        return ternary_map.get(ternary_option, False)

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

    def migrate_analysis_panels(self, old_panels):
        return None if old_panels is None else [self.migrate_analysis_panel(old_panel=old_panel)
                                                for old_panel in old_panels]

    def migrate_analysis_panel(self, old_panel):
        new_panel = self.convert_class(self.new_model.AnalysisPanel, old_panel)
        new_panel.review_outcome = old_panel.reviewOutcome
        new_panel.multiple_genetic_origins = old_panel.multipleGeneticOrigins
        return self.validate_object(object_to_validate=new_panel, object_type=self.new_model.AnalysisPanel)

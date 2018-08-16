import logging

from protocols import reports_4_0_0 as reports_4_0_0
from protocols import reports_3_0_0 as reports_3_0_0
from protocols.migration.base_migration import BaseMigration
from protocols.migration.base_migration import MigrationError


class MigrateReports400To300(BaseMigration):

    old_model = reports_4_0_0
    new_model = reports_3_0_0

    def migrate_clinical_report_rd(self, old_instance):
        """
        :type old_instance: reports_4_0_0.ClinicalReportRD
        :rtype: reports_3_0_0.ClinicalReportRD
        """
        new_instance = self.convert_class(self.new_model.ClinicalReportRD, old_instance)

        # interpretationRequestId changed to interpretationRequestID
        new_instance.interpretationRequestID = old_instance.interpretationRequestId

        # interpretationRequestAnalysisVersion can be null in version 4
        if hasattr(old_instance, 'interpretationRequestAnalysisVersion') and old_instance.interpretationRequestAnalysisVersion is not None:
            new_instance.interpretationRequestAnalysisVersion = old_instance.interpretationRequestAnalysisVersion
        else:
            new_instance.interpretationRequestAnalysisVersion = old_instance.interpretationRequestVersion

        new_instance.candidateVariants = self.migrate_reported_variants(old_variants=old_instance.candidateVariants)
        new_instance.candidateStructuralVariants = self.migrate_reported_structural_variants(old_structural_variants=old_instance.candidateStructuralVariants)

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ClinicalReportRD)

    def migrate_reported_variants(self, old_variants):
        if old_variants is None:
            return old_variants
        return [self.migrate_reported_variant(old_variant) for old_variant in old_variants]

    def migrate_reported_variant(self, old_reported_variant):
        new_reported_variant = self.convert_class(self.new_model.ReportedVariant, old_reported_variant)
        new_reported_variant.dbSNPid = old_reported_variant.dbSnpId
        new_reported_variant.calledGenotypes = self.migrate_called_genotypes(old_called_genotypes=old_reported_variant.calledGenotypes)
        new_reported_variant.reportEvents = self.migrate_report_events(old_reported_variant.reportEvents)

        return self.validate_object(object_to_validate=new_reported_variant, object_type=self.new_model.ReportedVariant)

    def migrate_reported_structural_variants(self, old_structural_variants):
        if old_structural_variants is None:
            return old_structural_variants
        return [self.migrate_reported_structural_variant(old_structural_variant) for old_structural_variant in old_structural_variants]

    def migrate_reported_structural_variant(self, old_structural_variant):
        new_reported_structural_variant = self.convert_class(self.new_model.ReportedStructuralVariant, old_structural_variant)
        new_reported_structural_variant.calledGenotypes = self.migrate_called_genotypes(old_called_genotypes=old_structural_variant.calledGenotypes)
        new_reported_structural_variant.reportEvents = self.migrate_report_events(old_structural_variant.reportEvents)
        return self.validate_object(object_to_validate=new_reported_structural_variant, object_type=self.new_model.ReportedStructuralVariant)

    def migrate_called_genotypes(self, old_called_genotypes):
        return [self.migrate_called_genotype(old_genotype) for old_genotype in old_called_genotypes]

    def migrate_called_genotype(self, old_genotype):
        new_genotype = self.convert_class(self.new_model.CalledGenotype, old_genotype)
        return self.validate_object(object_to_validate=new_genotype, object_type=self.new_model.CalledGenotype)

    def migrate_report_events(self, old_events):
        if old_events is None:
            return None
        return [self.migrate_report_event(old_event=old_event) for old_event in old_events]

    def migrate_report_event(self, old_event):
        new_instance = self.convert_class(self.new_model.ReportEvent, old_event)
        new_instance.variantClassification = self.migrate_variant_classification(old_v_classification=old_event.variantClassification)
        new_instance.genomicFeature = self.migrate_genomic_feature(old_genomic_feature=old_event.genomicFeature)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ReportEvent)

    def migrate_variant_classification(self, old_v_classification):
        old_classification = self.old_model.VariantClassification
        new_classification = self.new_model.VariantClassification
        variant_classification_map = {
            old_classification.pathogenic_variant: new_classification.PATHOGENIC,
            old_classification.likely_pathogenic_variant: new_classification.LIKELY_PATHOGENIC,
            old_classification.variant_of_unknown_clinical_significance: new_classification.VUS,
            old_classification.likely_benign_variant: new_classification.LIKELY_BENIGN,
            old_classification.benign_variant: new_classification.BENIGN,
        }
        return variant_classification_map.get(old_v_classification)

    def migrate_genomic_feature(self, old_genomic_feature):
        new_genomic_feature = self.new_model.GenomicFeature(
            featureType=old_genomic_feature.featureType,
            ensemblId=old_genomic_feature.ensemblId,
            HGNC=old_genomic_feature.hgnc,
            other_ids=old_genomic_feature.otherIds,
        )
        return self.validate_object(object_to_validate=new_genomic_feature, object_type=self.new_model.GenomicFeature)

    def migrate_interpretation_request_rd(self, old_instance):
        """
        Migrates a reports_4_0_0.InterpretationRequestRD into a reports_3_0_0.InterpretationRequestRD
        :type old_instance: reports_3_0_0.InterpretationRequestRD
        :rtype: reports_6_0_0.InterpretationRequestRD
        """
        new_instance = self.convert_class(self.new_model.InterpretationRequestRD, old_instance)
        new_instance.versionControl = self.new_model.VersionControl()
        new_instance.InterpretationRequestID = old_instance.interpretationRequestId
        new_instance.InterpretationRequestVersion = old_instance.interpretationRequestVersion
        new_instance.TieringVersion = old_instance.tieringVersion
        new_instance.analysisReturnURI = old_instance.analysisReturnUri
        new_instance.TieredVariants = self.migrate_reported_variants(old_variants=old_instance.tieredVariants)
        new_instance.BAMs = self.migrate_files(old_files=old_instance.bams)
        new_instance.VCFs = self.migrate_files(old_files=old_instance.vcfs)
        new_instance.bigWigs = self.migrate_files(old_files=old_instance.bigWigs)
        new_instance.pedigreeDiagram = self.migrate_file(old_file=old_instance.pedigreeDiagram)
        new_instance.annotationFile = self.migrate_file(old_file=old_instance.annotationFile)
        new_instance.otherFiles = self.migrate_files(old_files=old_instance.otherFiles)
        new_instance.pedigree = self.migrate_pedigree(old_pedigree=old_instance.pedigree)

        # return new_instance
        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD
        )

    def migrate_pedigree(self, old_pedigree):
        """
        :param old_pedigree: org.gel.models.participant.avro.Pedigree 1.0.0
        :return: org.gel.models.report.avro RDParticipant.Pedigree 3.0.0
        """
        new_pedigree = self.convert_class(self.new_model.Pedigree, old_pedigree)
        new_pedigree.versionControl = self.new_model.VersionControl()
        new_pedigree.gelFamilyId = old_pedigree.familyId
        new_pedigree.analysisPanels = self.migrate_analysis_panels(old_panels=old_pedigree.analysisPanels)
        new_pedigree.participants = self.migrate_members_to_participants(old_members=old_pedigree.members, family_id=old_pedigree.familyId)
        return self.validate_object(object_to_validate=new_pedigree, object_type=self.new_model.Pedigree)

    def migrate_members_to_participants(self, old_members, family_id):
        return [self.migrate_member_to_participant(old_member=old_member, family_id=family_id) for old_member in old_members]

    def migrate_member_to_participant(self, old_member, family_id):
        new_participant = self.convert_class(self.new_model.RDParticipant, old_member)
        new_participant.gelFamilyId = family_id
        new_participant.pedigreeId = old_member.pedigreeId
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

        return self.validate_object(object_to_validate=new_participant, object_type=self.new_model.RDParticipant)

    @staticmethod
    def migrate_samples(old_samples):
        return None if old_samples is None else [old_sample.sampleId for old_sample in old_samples]

    def migrate_hpo_term_list(self, old_list):
        return None if old_list is None else [self.migrate_hpo_term(old_term=old_term) for old_term in old_list]

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
        return status_map.get(old_status)

    def migrate_life_status(self, old_status):
        status_map = {
            self.old_model.LifeStatus.ABORTED: self.new_model.LifeStatus.aborted,
            self.old_model.LifeStatus.ALIVE: self.new_model.LifeStatus.alive,
            self.old_model.LifeStatus.DECEASED: self.new_model.LifeStatus.deceased,
            self.old_model.LifeStatus.UNBORN: self.new_model.LifeStatus.unborn,
            self.old_model.LifeStatus.STILLBORN: self.new_model.LifeStatus.stillborn,
            self.old_model.LifeStatus.MISCARRIAGE: self.new_model.LifeStatus.miscarriage,
        }
        return status_map.get(old_status)

    def migrate_adopted_status(self, old_status):
        status_map = {
            self.old_model.AdoptedStatus.notadopted: self.new_model.AdoptedStatus.not_adopted,
            self.old_model.AdoptedStatus.adoptedin: self.new_model.AdoptedStatus.adoptedin,
            self.old_model.AdoptedStatus.adoptedout: self.new_model.AdoptedStatus.adoptedout,
        }
        return status_map.get(old_status)

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
        return None if old_panels is None else [self.migrate_analysis_panel(old_panel=old_panel) for old_panel in old_panels]

    def migrate_analysis_panel(self, old_panel):
        new_panel = self.convert_class(self.new_model.AnalysisPanel, old_panel)
        new_panel.review_outcome = old_panel.reviewOutcome
        new_panel.multiple_genetic_origins = old_panel.multipleGeneticOrigins
        return self.validate_object(object_to_validate=new_panel, object_type=self.new_model.AnalysisPanel)

    def migrate_files(self, old_files):
        if old_files is None:
            return None
        if isinstance(old_files, list):
            return [self.migrate_file(old_file=old_file) for old_file in old_files]
        elif isinstance(old_files, dict):
            return {key: self.migrate_file(old_file=old_file) for (key, old_file) in old_files.items()}

    def migrate_file(self, old_file):
        if old_file is None:
            return None
        sample_id = old_file.sampleId

        md5_sum = self.new_model.File(
            SampleId=None,
            md5Sum=None,
            URIFile=old_file.md5Sum,
            fileType=self.new_model.FileType.MD5Sum
        )

        invalid_file_types = [
            self.old_model.FileType.PARTITION,
            self.old_model.FileType.VARIANT_FREQUENCIES,
            self.old_model.FileType.COVERAGE,
        ]
        file_type = old_file.fileType if old_file.fileType not in invalid_file_types else self.new_model.FileType.OTHER

        new_file = self.new_model.File(
                fileType=file_type,
                URIFile=old_file.uriFile,
                SampleId=sample_id,
                md5Sum=md5_sum,
            )
        return self.validate_object(object_to_validate=new_file, object_type=self.new_model.File)

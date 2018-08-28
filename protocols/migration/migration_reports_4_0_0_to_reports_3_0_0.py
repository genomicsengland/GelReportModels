import logging

from protocols import reports_4_0_0 as reports_4_0_0
from protocols import reports_3_0_0 as reports_3_0_0
from protocols.migration.base_migration import BaseMigration
from protocols.migration.base_migration import MigrationError
from protocols.migration.participants import MigrationParticipants100ToReports


class MigrateReports400To300(BaseMigration):

    old_model = reports_4_0_0
    new_model = reports_3_0_0

    def migrate_interpretation_request_rd(self, old_instance):
        """
        Migrates a reports_4_0_0.InterpretationRequestRD into a reports_3_0_0.InterpretationRequestRD
        :type old_instance: reports_4_0_0.InterpretationRequestRD
        :rtype: reports_3_0_0.InterpretationRequestRD
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
        new_instance.pedigree = MigrationParticipants100ToReports().migrate_pedigree(old_pedigree=old_instance.pedigree)

        # return new_instance
        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD
        )

    def migrate_interpreted_genome_rd(self, old_instance):
        """
        :type old_instance: reports_4_0_0.InterpretedGenomeRD
        :rtype: reports_3_0_0.InterpretedGenomeRD
        """
        new_instance = self.convert_class(self.new_model.InterpretedGenomeRD, old_instance)
        new_instance.versionControl = self.new_model.VersionControl()
        new_instance.reportedVariants = self.migrate_reported_variants(old_variants=old_instance.reportedVariants)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.InterpretedGenomeRD)

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

    def migrate_exit_questionnaire_rd(self, old_instance):
        """
        :type old_instance: reports_4_0_0.RareDiseaseExitQuestionnaire
        :rtype: reports_3_0_0.RareDiseaseExitQuestionnaire
        """
        new_instance = self.convert_class(self.new_model.RareDiseaseExitQuestionnaire, old_instance)
        return self.validate_object(object_to_validate=new_instance,
                                    object_type=self.new_model.RareDiseaseExitQuestionnaire)

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
        if new_instance.eventJustification is None:
            new_instance.eventJustification = ""
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

import logging

from protocols import reports_4_0_0 as reports_4_0_0
from protocols import reports_3_0_0 as reports_3_0_0
from protocols.migration.base_migration import BaseMigration
from protocols.migration.base_migration import MigrationError
from protocols.migration import MigrationParticipants100ToReports


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
        new_instance.TieredVariants = self.convert_collection(
            list(zip(old_instance.tieredVariants, new_instance.TieredVariants)), self._migrate_reported_variant)
        new_instance.BAMs = self.convert_collection(old_instance.bams, self._migrate_file)
        new_instance.VCFs = self.convert_collection(old_instance.vcfs, self._migrate_file)
        new_instance.bigWigs = self.convert_collection(old_instance.bigWigs, self._migrate_file)
        new_instance.pedigreeDiagram = self._migrate_file(old_file=old_instance.pedigreeDiagram)
        new_instance.annotationFile = self._migrate_file(old_file=old_instance.annotationFile)
        new_instance.otherFiles = self.convert_collection(old_instance.otherFiles, self._migrate_file)
        new_instance.pedigree = MigrationParticipants100ToReports().migrate_pedigree(old_instance=old_instance.pedigree)

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
        new_instance.reportedVariants = self.convert_collection(
            list(zip(old_instance.reportedVariants, new_instance.reportedVariants)), self._migrate_reported_variant)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.InterpretedGenomeRD)

    def migrate_clinical_report_rd(self, old_instance):
        """
        :type old_instance: reports_4_0_0.ClinicalReportRD
        :rtype: reports_3_0_0.ClinicalReportRD
        """
        new_instance = self.convert_class(self.new_model.ClinicalReportRD, old_instance)

        # interpretationRequestAnalysisVersion can be null in version 4
        if hasattr(old_instance, 'interpretationRequestAnalysisVersion') and old_instance.interpretationRequestAnalysisVersion is not None:
            new_instance.interpretationRequestAnalysisVersion = old_instance.interpretationRequestAnalysisVersion
        else:
            new_instance.interpretationRequestAnalysisVersion = old_instance.interpretationRequestVersion

        if old_instance.candidateVariants is not None:
            new_instance.candidateVariants = self.convert_collection(
                list(zip(old_instance.candidateVariants, new_instance.candidateVariants)), self._migrate_reported_variant)
        new_instance.candidateStructuralVariants = self.convert_collection(
            old_instance.candidateStructuralVariants, self._migrate_reported_structural_variant)

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ClinicalReportRD)

    def migrate_exit_questionnaire_rd(self, old_instance):
        """
        :type old_instance: reports_4_0_0.RareDiseaseExitQuestionnaire
        :rtype: reports_3_0_0.RareDiseaseExitQuestionnaire
        """
        new_instance = self.convert_class(self.new_model.RareDiseaseExitQuestionnaire, old_instance)
        return self.validate_object(object_to_validate=new_instance,
                                    object_type=self.new_model.RareDiseaseExitQuestionnaire)

    def _migrate_reported_variant(self, reported_variants):
        old_instance = reported_variants[0]
        new_instance = reported_variants[1]
        new_instance.reportEvents = self.convert_collection(
            list(zip(old_instance.reportEvents, new_instance.reportEvents)), self._migrate_report_event)
        return new_instance

    def _migrate_reported_structural_variant(self, old_structural_variant):
        new_instance = self.convert_class(self.new_model.ReportedStructuralVariant, old_structural_variant)
        new_instance.reportEvents = self.convert_collection(
            list(zip(old_structural_variant.reportEvents, new_instance.reportEvents)), self._migrate_report_event)
        return new_instance

    def _migrate_report_event(self, report_events):
        old_instance = report_events[0]
        new_instance = report_events[1]
        new_instance.variantClassification = self._migrate_variant_classification(
            old_v_classification=old_instance.variantClassification)
        if new_instance.eventJustification is None:
            new_instance.eventJustification = ""
        return new_instance

    def _migrate_variant_classification(self, old_v_classification):
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

    def _migrate_file(self, old_file):
        if old_file is None:
            return None
        if isinstance(old_file.sampleId, list) and len(old_file.sampleId) == 1:
            sample_id = old_file.sampleId[0]
        else:
            sample_id = old_file.sampleId

        if old_file.md5Sum:
            md5_sum = self.new_model.File(
                SampleId=None,
                md5Sum=None,
                URIFile=old_file.md5Sum,
                fileType=self.new_model.FileType.MD5Sum
            )
        else:
            md5_sum = None

        invalid_file_types = [
            self.old_model.FileType.PARTITION,
            self.old_model.FileType.VARIANT_FREQUENCIES,
            self.old_model.FileType.COVERAGE,
        ]
        file_type = old_file.fileType if old_file.fileType not in invalid_file_types else self.new_model.FileType.OTHER

        new_instance = self.new_model.File(
                fileType=file_type,
                URIFile=old_file.uriFile,
                SampleId=sample_id,
                md5Sum=md5_sum,
            )
        return new_instance

from protocols import reports_3_0_0
from protocols import reports_4_0_0
from protocols.migration import BaseMigration
from protocols.migration import MigrationReports3ToParticipant1


class MigrateReports3To4(BaseMigration):

    old_model = reports_3_0_0
    new_model = reports_4_0_0
    re_counter = 1
    participants_migrator = MigrationReports3ToParticipant1()
    variant_classification_map = {
        old_model.VariantClassification.PATHOGENIC: new_model.VariantClassification.pathogenic_variant,
        old_model.VariantClassification.LIKELY_PATHOGENIC: new_model.VariantClassification.likely_pathogenic_variant,
        old_model.VariantClassification.VUS: new_model.VariantClassification.variant_of_unknown_clinical_significance,
        old_model.VariantClassification.LIKELY_BENIGN: new_model.VariantClassification.likely_benign_variant,
        old_model.VariantClassification.BENIGN: new_model.VariantClassification.benign_variant,
    }

    def migrate_interpretation_request_rd(self, old_instance):
        """
        :type old_instance: reports_3_0_0.InterpretationRequestRD
        :rtype: reports_4_0_0.InterpretationRequestRD
        """
        new_instance = self.convert_class(self.new_model.InterpretationRequestRD, old_instance)
        new_instance.bams = self.convert_collection(
            list(zip(old_instance.BAMs, new_instance.bams)), self._migrate_file)
        new_instance.vcfs = self.convert_collection(
            list(zip(old_instance.VCFs, new_instance.vcfs)), self._migrate_file)
        if old_instance.bigWigs is not None:
            new_instance.bigWigs = self.convert_collection(
                list(zip(old_instance.bigWigs, new_instance.bigWigs)), self._migrate_file)
        new_instance.pedigreeDiagram = self._migrate_file((old_instance.pedigreeDiagram, new_instance.pedigreeDiagram))
        new_instance.annotationFile = self._migrate_file((old_instance.annotationFile, new_instance.annotationFile))
        if old_instance.otherFiles is not None:
            new_instance.otherFiles = self.convert_collection(
                {k: (old_file, new_instance.otherFiles[k]) for k, old_file in old_instance.otherFiles.items()},
                self._migrate_file)
        new_instance.tieredVariants = self.convert_collection(
            list(zip(old_instance.TieredVariants, new_instance.tieredVariants)), self._migrate_reported_variant)
        new_instance.pedigree = self.participants_migrator.migrate_pedigree(
            pedigree=old_instance.pedigree, ldp_code=next(iter(old_instance.workspace), None))
        new_instance.internalStudyId = ''
        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD
        )

    def migrate_interpreted_genome_rd(self, old_instance):
        """
        :type old_instance: reports_3_0_0.InterpretedGenomeRD
        :rtype: reports_4_0_0.InterpretedGenomeRD
        """
        new_instance = self.convert_class(self.new_model.InterpretedGenomeRD, old_instance)
        new_instance.reportedVariants = self.convert_collection(
            list(zip(old_instance.reportedVariants, new_instance.reportedVariants)), self._migrate_reported_variant)
        new_instance.reportedStructuralVariants = self.convert_collection(
            old_instance.reportedStructuralVariants, self._migrate_reported_structural_variant)
        return self.validate_object(new_instance, self.new_model.InterpretedGenomeRD)

    def migrate_clinical_report_rd(self, old_instance):
        """
        :type old_instance: reports_3_0_0.ClinicalReportRD
        :rtype: reports_4_0_0.ClinicalReportRD
        """
        new_instance = self.convert_class(self.new_model.ClinicalReportRD, old_instance)
        if old_instance.candidateVariants is not None:
            new_instance.candidateVariants = self.convert_collection(
                list(zip(old_instance.candidateVariants, new_instance.candidateVariants)), self._migrate_reported_variant)
        new_instance.candidateStructuralVariants = self.convert_collection(
            old_instance.candidateStructuralVariants, self._migrate_reported_structural_variant)
        return self.validate_object(new_instance, self.new_model.InterpretedGenomeRD)

    def migrate_rd_exit_questionnaire(self, old_instance):
        """
        :type old_instance: reports_3_0_0.RareDiseaseExitQuestionnaire
        :rtype: reports_4_0_0.RareDiseaseExitQuestionnaire
        """
        new_instance = self.convert_class(
            self.new_model.RareDiseaseExitQuestionnaire,
            old_instance)  # type: reports_4_0_0.RareDiseaseExitQuestionnaire
        return self.validate_object(new_instance, self.new_model.RareDiseaseExitQuestionnaire)

    def _migrate_reported_variant(self, reported_variant):
        old_instance = reported_variant[0]
        new_instance = reported_variant[1]
        new_instance.reportEvents = self.convert_collection(
            list(zip(old_instance.reportEvents, new_instance.reportEvents)), self._migrate_report_event)
        return new_instance

    def _migrate_reported_structural_variant(self, old_instance):
        new_instance = self.convert_class(self.new_model.ReportedStructuralVariant, old_instance)
        new_instance.reportEvents = self.convert_collection(
            list(zip(old_instance.reportEvents, new_instance.reportEvents)), self._migrate_report_event)
        return new_instance

    def _migrate_report_event(self, report_event):
        old_instance = report_event[0]
        new_instance = report_event[1]
        new_instance.genomicFeature.hgnc = old_instance.genomicFeature.HGNC
        new_instance.variantClassification = self.variant_classification_map.get(
            old_instance.variantClassification, self.new_model.VariantClassification.not_assessed
        )
        return new_instance

    def _migrate_file(self, files):
        old_instance = files[0]
        new_instance = files[1]
        if old_instance is None:
            return None
        if isinstance(old_instance.SampleId, list):
            sample_id = old_instance.SampleId
        elif old_instance.SampleId is None:
            sample_id = None
        else:
            sample_id = [old_instance.SampleId]
        new_instance.sampleId = sample_id
        return new_instance

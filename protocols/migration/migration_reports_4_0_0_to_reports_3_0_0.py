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

        if hasattr(old_instance, 'candidateVariants') and old_instance.candidateVariants is not None:
            new_instance.candidateVariants = self.migrate_reported_variants(old_variants=old_instance.candidateVariants)
        if hasattr(old_instance, 'candidateStructuralVariants') and old_instance.candidateStructuralVariants is not None:
            new_instance.candidateStructuralVariants = self.migrate_reported_structural_variants(old_structural_variants=old_instance.candidateStructuralVariants)

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ClinicalReportRD)

    def migrate_reported_variants(self, old_variants):
        return [self.migrate_reported_variant(old_variant) for old_variant in old_variants]

    def migrate_reported_variant(self, old_reported_variant):
        new_reported_variant = self.convert_class(self.new_model.ReportedVariant, old_reported_variant)
        new_reported_variant.dbSNPid = old_reported_variant.dbSnpId
        new_reported_variant.calledGenotypes = self.migrate_called_genotypes(old_called_genotypes=old_reported_variant.calledGenotypes)
        new_reported_variant.reportEvents = self.migrate_report_events(old_reported_variant.reportEvents)

        return self.validate_object(object_to_validate=new_reported_variant, object_type=self.new_model.ReportedVariant)

    def migrate_reported_structural_variants(self, old_structural_variants):
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

    def migrate_report_events(self, old_report_events):
        return [self.migrate_report_event(old_report_event) for old_report_event in old_report_events]

    def migrate_report_event(self, old_report_event):
        new_report_event = self.convert_class(self.new_model.ReportEvent, old_report_event)
        new_report_event.genomicFeature = self.migrate_genomic_feature(old_report_event.genomicFeature)
        if old_report_event.variantClassification is not None:
            new_report_event.variantClassification = self.migrate_variant_classification(old_report_event.variantClassification)
        return self.validate_object(object_to_validate=new_report_event, object_type=self.new_model.ReportEvent)

    def migrate_variant_classification(self, old_classification):
        variant_classification_map = {
            self.old_model.VariantClassification.benign_variant: self.new_model.VariantClassification.BENIGN,
            self.old_model.VariantClassification.likely_benign_variant: self.new_model.VariantClassification.LIKELY_BENIGN,
            self.old_model.VariantClassification.variant_of_unknown_clinical_significance : self.new_model.VariantClassification.VUS,
            self.old_model.VariantClassification.likely_pathogenic_variant: self.new_model.VariantClassification.LIKELY_PATHOGENIC,
            self.old_model.VariantClassification.pathogenic_variant: self.new_model.VariantClassification.PATHOGENIC,
        }
        return variant_classification_map.get(old_classification)

    def migrate_genomic_feature(self, old_genomic_feature):
        new_genomic_feature = self.new_model.GenomicFeature(
            featureType=old_genomic_feature.featureType,
            ensemblId=old_genomic_feature.ensemblId,
            HGNC=old_genomic_feature.hgnc,
            other_ids=old_genomic_feature.otherIds,
        )
        return self.validate_object(object_to_validate=new_genomic_feature, object_type=self.new_model.GenomicFeature)

from protocols import reports_4_0_0
from protocols import reports_4_2_0
from protocols.migration import BaseMigration
from protocols.migration.participants import MigrationParticipants103To100


class MigrateReports420To400(BaseMigration):
    """
    We only need migration from 4.2.0 to 4.0.0 to send cancer cases to Illumina.
    Illumina will be returning ClinicalReports in version 4.0.0.
    We don't need to migrate any rare disease case.

    This target schema is missing the attribute `groupOfVariants`, this means we will lose the information related
    to composite heterozygous variants.
    The target schema is missing the list of `VariantCall` that includes the important attribute `sampleId`. This means
    we will lose the ability to represent multiple variant calls for the same ReportEvent and furthermore we lose the
    reference to the sampleId in the ReportedVariant.
    """
    old_model = reports_4_2_0
    new_model = reports_4_0_0

    def migrate_cancer_interpretation_request(self, cancer_interpretation_request):
        """
        :type cancer_interpretation_request: reports_4_2_0.CancerInterpretationRequest
        :rtype: reports_4_0_0.CancerInterpretationRequest
        """
        new_cancer_interpretation_request = self.new_model.CancerInterpretationRequest.fromJsonDict(
            jsonDict=cancer_interpretation_request.toJsonDict()
        )

        new_cancer_interpretation_request.gitVersionControl = "4.0.0"

        new_cancer_participant = MigrationParticipants103To100().migrate_cancer_participant(
            cancer_participant=cancer_interpretation_request.cancerParticipant
        )
        new_cancer_interpretation_request.cancerParticipant = new_cancer_participant

        new_reported_somatic_variants_list = []
        for structural_tiered_variant in cancer_interpretation_request.tieredVariants:
            new_reported_somatic_variants_list.append(
                self.migrate_reported_variant_cancer(
                    structural_tiered_variant
                )
            )
        new_cancer_interpretation_request.tieredVariants = new_reported_somatic_variants_list

        new_reported_somatic_structural_variants_list = []
        for structural_tiered_variant in cancer_interpretation_request.structuralTieredVariants:
            new_reported_somatic_structural_variants_list.append(
                self.migrate_reported_structural_variant_cancer(
                    structural_tiered_variant
                )
            )
        new_cancer_interpretation_request.structuralTieredVariants = new_reported_somatic_structural_variants_list

        return self.validate_object(
            object_to_validate=new_cancer_interpretation_request, object_type=self.new_model.CancerInterpretationRequest
        )

    def migrate_reported_variant_cancer(self, reported_variant_cancer):
        """
        This migration gets the information from the first variant call, all other information will be lost.
        :type reported_variant_cancer: reports_4_2_0.ReportedVariantCancer
        :rtype: reports_4_0_0.ReportedSomaticVariants
        """
        new_reported_somatic_variants = self.new_model.ReportedSomaticVariants()
        new_reported_variant_cancer = self.new_model.ReportedVariantCancer.fromJsonDict(
            jsonDict=reported_variant_cancer.toJsonDict()
        )
        new_reported_variant_cancer.cDnaChange = reported_variant_cancer.cdnaChange
        if reported_variant_cancer.variantCalls is not None and len(reported_variant_cancer.variantCalls) > 0:
            variant_call = reported_variant_cancer.variantCalls[0]
            new_reported_variant_cancer.depthReference = variant_call.depthReference
            new_reported_variant_cancer.depthAlternate = variant_call.depthAlternate
            new_reported_variant_cancer.vaf = variant_call.vaf
        new_reported_somatic_variants.reportedVariantCancer = new_reported_variant_cancer
        report_events = []
        if reported_variant_cancer.reportEvents is not None:
            for report_event in reported_variant_cancer.reportEvents:
                report_events.append(self.migrate_report_event_cancer(report_event))
        new_reported_variant_cancer.reportEvents = report_events
        new_reported_somatic_variants.alleleOrigins = reported_variant_cancer.alleleOrigins

        return self.validate_object(
            object_to_validate=new_reported_somatic_variants, object_type=self.new_model.ReportedSomaticVariants
        )

    def migrate_reported_structural_variant_cancer(self, reported_structural_variant_cancer):
        """
        :type reported_variant_cancer: reports_4_2_0.ReportedStructuralVariantCancer
        :rtype: reports_4_0_0.ReportedSomaticStructuralVariants
        """
        new_reported_somatic_structural_variants = self.new_model.ReportedSomaticStructuralVariants()
        new_reported_structural_variant_cancer = self.new_model.ReportedStructuralVariant.fromJsonDict(
            jsonDict=reported_structural_variant_cancer.toJsonDict()
        )
        new_reported_somatic_structural_variants.reportedStructuralVariantCancer = new_reported_structural_variant_cancer
        new_reported_somatic_structural_variants.alleleOrigins = reported_structural_variant_cancer.alleleOrigins

        return self.validate_object(
            object_to_validate=new_reported_somatic_structural_variants, object_type=self.new_model.ReportedSomaticStructuralVariants
        )

    def migrate_report_event_cancer(self, report_event_cancer):
        """
        This migration is missing the attribute `groupOfVariants`, this means we will lose the information related
        to composite heterozygous variants.
        :type report_event_cancer: reports_4_2_0.ReportEventCancer
        :rtype: reports_4_0_0.ReportEventCancer
        """
        new_report_event_cancer = self.new_model.ReportEventCancer.fromJsonDict(
            jsonDict=report_event_cancer.toJsonDict()
        )
        new_actions = []
        if report_event_cancer.actions is not None:
            for action in report_event_cancer.actions:
                new_actions.append(self.migrate_action(action))
        new_report_event_cancer.actions = new_actions
        new_report_event_cancer.genomicFeatureCancer = self.migrate_genomic_feature_cancer(
            report_event_cancer.genomicFeatureCancer
        )

        return self.validate_object(
            object_to_validate=new_report_event_cancer,
            object_type=self.new_model.ReportEventCancer
        )

    def migrate_genomic_feature_cancer(self, genomic_feature_cancer):
        """
        :type genomic_feature_cancer: reports_4_2_0.GenomicFeatureCancer
        :rtype: reports_4_0_0.GenomicFeatureCancer
        """
        new_genomic_feature_cancer = self.new_model.GenomicFeatureCancer.fromJsonDict(
            jsonDict=genomic_feature_cancer.toJsonDict()
        )
        feature_type_map = {
            reports_4_2_0.FeatureTypeCancer.gene: reports_4_0_0.FeatureTypes.Gene,
            reports_4_2_0.FeatureTypeCancer.regulatory_region: reports_4_0_0.FeatureTypes.RegulatoryRegion,
            reports_4_2_0.FeatureTypeCancer.transcript: reports_4_0_0.FeatureTypes.Transcript,
        }
        new_genomic_feature_cancer.featureType = feature_type_map[genomic_feature_cancer.featureType]
        role_in_cancer_map = {
            None: None,
            reports_4_2_0.RoleInCancer.oncogene: reports_4_0_0.RoleInCancer.oncogene,
            reports_4_2_0.RoleInCancer.tumor_suppressor_gene: reports_4_0_0.RoleInCancer.TSG,
            reports_4_2_0.RoleInCancer.both: reports_4_0_0.RoleInCancer.both
        }
        new_genomic_feature_cancer.roleInCancer = role_in_cancer_map[genomic_feature_cancer.roleInCancer]

        return self.validate_object(
            object_to_validate=new_genomic_feature_cancer,
            object_type=self.new_model.GenomicFeatureCancer
        )

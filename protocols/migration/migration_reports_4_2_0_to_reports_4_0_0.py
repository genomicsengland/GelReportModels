from protocols import reports_4_0_0
from protocols import reports_4_2_0
from protocols.migration import BaseMigration
from protocols.migration.participants import MigrationParticipants104To100


class MigrateReports420To400(BaseMigration):

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

        new_cancer_participant = MigrationParticipants104To100().migrate_cancer_participant(
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
        # TODO: migrate report events
        new_reported_variant_cancer.reportEvents = []
        new_reported_somatic_variants.reportedVariantCancer = new_reported_variant_cancer
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

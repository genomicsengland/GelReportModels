from protocols import reports_4_0_0 as reports_4_0_0
from protocols import reports_4_2_0
from protocols.migration import BaseMigration
from protocols.migration.participants import MigrationParticipants100To104


class MigrateReports400To420(BaseMigration):

    old_model = reports_4_0_0
    new_model = reports_4_2_0

    def migrate_cancer_interpretation_request(self, cancer_interpretation_request, sample_id):
        """
        :type cancer_interpretation_request: reports_4_0_0.CancerInterpretationRequest
        :type sample_id: str
        :rtype: reports_4_2_0.CancerInterpretationRequest
        """
        new_cancer_interpretation_request = self.new_model.CancerInterpretationRequest.fromJsonDict(
            jsonDict=cancer_interpretation_request.toJsonDict()
        )

        new_cancer_interpretation_request.gitVersionControl = "4.2.0"

        new_cancer_participant = MigrationParticipants100To104().migrate_cancer_participant(
            cancer_participant=cancer_interpretation_request.cancerParticipant
        )
        new_cancer_interpretation_request.cancerParticipant = new_cancer_participant

        # FIXME: we are using a sample_id received as a parameter, models need to be changed
        tiered_variants = []
        for reported_variant in cancer_interpretation_request.tieredVariants:
            tiered_variants.append(self.migrate_reported_variant_cancer(
                reported_variant,
                sample_id
            ))
        new_cancer_interpretation_request.tieredVariants = tiered_variants

        # FIXME: we have no sample id field in the structural variant
        structural_tiered_variants = []
        for reported_structural_variant in cancer_interpretation_request.structuralTieredVariants:
            structural_tiered_variants.append(self.migrate_reported_structural_variant_cancer(
                reported_structural_variant
            ))
        new_cancer_interpretation_request.structuralTieredVariants = structural_tiered_variants

        return self.validate_object(
            object_to_validate=new_cancer_interpretation_request, object_type=self.new_model.CancerInterpretationRequest
        )

    def migrate_cancer_interpreted_genome(self, cancer_interpreted_genome, sample_id):
        """
        :type cancer_interpreted_genome: reports_4_0_0.CancerInterpretedGenome
        :type sample_id: str
        :rtype: reports_4_2_0.CancerInterpretedGenome
        """
        new_cancer_interpreted_genome = self.new_model.CancerInterpretedGenome.fromJsonDict(
            jsonDict=cancer_interpreted_genome.toJsonDict()
        )

        new_cancer_interpreted_genome.gitVersionControl = "4.2.0"

        # FIXME: we are using the individual identifier in the cancer participant to set the sample id
        reported_variants = []
        for reported_variant in cancer_interpreted_genome.reportedVariants:
            reported_variants.append(self.migrate_reported_variant_cancer(
                reported_variant,
                sample_id
            ))
        new_cancer_interpreted_genome.reportedVariants = reported_variants

        # FIXME: we have no sample id field in the structural variant
        structural_reported_variants = []
        for reported_structural_variant in cancer_interpreted_genome.reportedStructuralVariants:
            structural_reported_variants.append(self.migrate_reported_structural_variant_cancer(reported_structural_variant))
        new_cancer_interpreted_genome.reportedStructuralVariants = structural_reported_variants

        return self.validate_object(
            object_to_validate=new_cancer_interpreted_genome, object_type=self.new_model.CancerInterpretedGenome
        )

    def migrate_cancer_clinical_report(self, cancer_clinical_report, sample_id):
        """
        :type cancer_clinical_report: reports_4_0_0.ClinicalReportCancer
        :type sample_id: str
        :rtype: reports_4_2_0.ClinicalReportCancer
        """
        new_cancer_clinical_report = self.new_model.ClinicalReportCancer.fromJsonDict(
            jsonDict=cancer_clinical_report.toJsonDict()
        )

        # FIXME: we are using the individual identifier in the cancer participant to set the sample id
        candidate_variants = []
        for candidate_variant in cancer_clinical_report.candidateVariants:
            candidate_variants.append(self.migrate_reported_variant_cancer(
                candidate_variant,
                sample_id
            ))
        new_cancer_clinical_report.reportedVariants = candidate_variants

        # FIXME: we have no sample id field in the structural variant
        structural_candidate_variants = []
        for candidate_structural_variant in cancer_clinical_report.candidateStructuralVariants:
            structural_candidate_variants.append(self.migrate_reported_structural_variant_cancer(candidate_structural_variant))
        new_cancer_clinical_report.reportedStructuralVariants = structural_candidate_variants

        return self.validate_object(
            object_to_validate=new_cancer_clinical_report, object_type=self.new_model.ClinicalReportCancer
        )

    def migrate_reported_variant_cancer(self, reported_somatic_variants, sample_id):
        """
        Migrates a ReportedSomaticVariants to a ReportedVariantCancer
        The sample id is required, otherwise the resulting object is not valid.
        :type reported_somatic_variants: reports_4_0_0.ReportedSomaticVariants
        :type sample_id: str
        :rtype: reports_4_2_0.ReportedVariantCancer
        """
        new_reported_variant_cancer = self.new_model.ReportedVariantCancer.fromJsonDict(
            jsonDict=reported_somatic_variants.reportedVariantCancer.toJsonDict()
        )
        new_reported_variant_cancer.alleleOrigins = reported_somatic_variants.alleleOrigins

        new_reported_variant_cancer.cdnaChange = reported_somatic_variants.reportedVariantCancer.cDnaChange

        # Creates a single VariantCall object with the only info available
        new_variant_call = self.new_model.VariantCall()
        new_variant_call.sampleId = sample_id
        new_variant_call.depthReference = reported_somatic_variants.reportedVariantCancer.depthReference
        new_variant_call.depthAlternate = reported_somatic_variants.reportedVariantCancer.depthAlternate
        new_variant_call.vaf = reported_somatic_variants.reportedVariantCancer.vaf
        new_reported_variant_cancer.variantCalls = [new_variant_call]

        new_report_events = []
        for report_event in reported_somatic_variants.reportedVariantCancer.reportEvents:
            new_report_events.append(self.migrate_report_event(
                report_event=report_event
            ))
        new_reported_variant_cancer.reportEvents = new_report_events

        return self.validate_object(
            object_to_validate=new_reported_variant_cancer, object_type=self.new_model.ReportedVariantCancer
        )

    def migrate_report_event(self, report_event):
        """
        :type report_event: reports_4_0_0.ReportEventCancer
        :rtype: reports_4_2_0.ReportEventCancer
        """
        new_report_event = self.new_model.ReportEventCancer.fromJsonDict(
            jsonDict=report_event.toJsonDict()
        )

        new_report_event.genomicFeatureCancer = self.migrate_genomic_feature_cancer(
            genomic_feature_cancer=report_event.genomicFeatureCancer
        )

        new_actions = []
        if report_event.actions:
            for action in report_event.actions:
                new_actions.append(self.migrate_action(
                    action=action
                ))
            new_report_event.actions = new_actions

        return self.validate_object(
            object_to_validate=new_report_event, object_type=self.new_model.ReportEventCancer
        )

    def migrate_action_type(self, action_type):
        action_types_map = {
            self.old_model.ActionType.therapy: self.new_model.ActionType.therapy,
            self.old_model.ActionType.therapeutic: self.new_model.ActionType.therapeutic,
            self.old_model.ActionType.diagnosis: self.new_model.ActionType.diagnosis,
            self.old_model.ActionType.prognosis: self.new_model.ActionType.prognosis
        }
        new_action_type = action_types_map.get(action_type, None)

        if new_action_type is None:
            if self.new_model.ActionType.therapy in action_type.lower():
                new_action_type = self.new_model.ActionType.therapy
            elif self.new_model.ActionType.therapeutic in action_type.lower():
                new_action_type = self.new_model.ActionType.therapeutic
            elif self.new_model.ActionType.diagnosis in action_type.lower():
                new_action_type = self.new_model.ActionType.diagnosis
            elif self.new_model.ActionType.prognosis in action_type.lower():
                new_action_type = self.new_model.ActionType.prognosis

        return new_action_type

    def migrate_action(self, action):
        """
        :type action: reports_4_0_0.Action
        :rtype: reports_4_2_0.Action
        """
        new_action = self.new_model.Action.fromJsonDict(
            jsonDict=action.toJsonDict()
        )

        action_status_map = {
            "clinical": self.new_model.ActionStatus.clinical,
            "pre_clinical": self.new_model.ActionStatus.pre_clinical,
            "pre-clinical": self.new_model.ActionStatus.pre_clinical
        }

        new_action.actionType = self.migrate_action_type(action.actionType)
        new_action.evidences = action.evidence
        new_action.status = action_status_map.get(action.status, None)

        return self.validate_object(
            object_to_validate=new_action, object_type=self.new_model.Action
        )

    def migrate_genomic_feature_cancer(self, genomic_feature_cancer):
        """
        :type genomic_feature_cancer: reports_4_0_0.GenomicFeatureCancer
        :rtype: reports_4_2_0.GenomicFeatureCancer
        """
        new_genomic_feature_cancer = self.new_model.GenomicFeatureCancer.fromJsonDict(
            jsonDict=genomic_feature_cancer.toJsonDict()
        )

        feature_type_map = {
            "RegulatoryRegion": self.new_model.FeatureTypeCancer.regulatory_region,
            "Gene": self.new_model.FeatureTypeCancer.gene,
            "Transcript": self.new_model.FeatureTypeCancer.transcript
        }
        role_in_cancer_map = {
            "oncogene":self.new_model.RoleInCancer.oncogene,
            "TSG": self.new_model.RoleInCancer.tumor_suppressor_gene,
            "both": self.new_model.RoleInCancer.both
        }
        new_genomic_feature_cancer.featureType = feature_type_map.get(genomic_feature_cancer.featureType, None)
        new_genomic_feature_cancer.roleInCancer = role_in_cancer_map.get(genomic_feature_cancer.roleInCancer, None)

        return self.validate_object(
            object_to_validate=new_genomic_feature_cancer, object_type=self.new_model.GenomicFeatureCancer
        )

    def migrate_reported_structural_variant_cancer(self, reported_somatic_structural_variants):
        """
        Migrates a ReportedSomaticStructuralVariants to a ReportedStructuralVariantCancer
        :type reported_somatic_structural_variants: reports_4_0_0.ReportedSomaticStructuralVariants
        :rtype: reports_4_2_0.ReportedStructuralVariantCancer
        """
        new_reported_variant_cancer = self.new_model.ReportedStructuralVariantCancer.fromJsonDict(
            jsonDict=reported_somatic_structural_variants.reportedStructuralVariantCancer.toJsonDict()
        )
        new_reported_variant_cancer.alleleOrigins = reported_somatic_structural_variants.alleleOrigins

        return self.validate_object(
            object_to_validate=new_reported_variant_cancer, object_type=self.new_model.ReportedStructuralVariantCancer
        )

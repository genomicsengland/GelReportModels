from protocols import reports_3_0_0
from protocols import reports_4_0_0


class MigrateReports3To4(object):
    old_model = reports_3_0_0
    new_model = reports_4_0_0

    def migrate_reported_somatic_variants(self, old_reported_somatic_variants):
        """
        :type old_reported_somatic_variants: reports_3_0_0.ReportedSomaticVariants
        :rtype: reports_4_0_0.ReportedSomaticVariants
        """
        new_reported_somatic_variants = self.new_model.ReportedSomaticVariants()

        old_reported_variant_cancer = old_reported_somatic_variants.reportedVariantCancer
        new_reported_somatic_variants.reportedVariantCancer = self.new_model.ReportedVariantCancer(
            clinVarIds=[''],
            additionalNumericVariantAnnotations=old_reported_variant_cancer.additionalNumericVariantAnnotations,
            additionalTextualVariantAnnotations=old_reported_variant_cancer.additionalTextualVariantAnnotations,
            vaf=old_reported_variant_cancer.VAF,
            cosmicIds=old_reported_variant_cancer.CosmicIds,
            ihp=old_reported_variant_cancer.IHP,
            alternate=old_reported_variant_cancer.alternate,
            cDnaChange=old_reported_variant_cancer.cDNAchange,
            chromosome=old_reported_variant_cancer.chromosome,
            comments=old_reported_variant_cancer.comments,
            commonAf=old_reported_variant_cancer.commonAF,
            dbSnpId=old_reported_variant_cancer.dbSNPid,
            depthAlternate=old_reported_variant_cancer.depthAlternate,
            depthReference=old_reported_variant_cancer.depthReference,
            position=old_reported_variant_cancer.position,
            proteinChange=old_reported_variant_cancer.proteinChange,
            reference=old_reported_variant_cancer.reference,
            reportEvents=old_reported_variant_cancer.reportEvents,
        )

        # TODO(Greg): Need to migrate each [event for event in reportEvents]

        allele_origins_map = {
            reports_3_0_0.SomaticOrGermline.somatic: reports_4_0_0.AlleleOrigin.somatic_variant,
            reports_3_0_0.SomaticOrGermline.germline: reports_4_0_0.AlleleOrigin.germline_variant,
        }
        old_variant = old_reported_somatic_variants.somaticOrGermline
        new_reported_somatic_variants.alleleOrigins = [allele_origins_map.get(old_variant)]

        new_report_events_cancer = [
            self.migrate_report_event_cancer(event) for event in old_reported_variant_cancer.reportEvents
        ]
        new_reported_somatic_variants.reportedVariantCancer.reportEvents = new_report_events_cancer

        if new_reported_somatic_variants.validate(new_reported_somatic_variants.toJsonDict()):
            return new_reported_somatic_variants
        else:
            # TODO(Greg): Improve these error messages
            raise Exception('This model can not be converted: ', new_reported_somatic_variants.validate_parts())

    def migrate_report_event_cancer(self, old_report_event_cancer):

        new_report_event_cancer = self.new_model.ReportEventCancer(
            eventJustification='',
            soTerms=[],
            actions=old_report_event_cancer.actions,
            genomicFeatureCancer=old_report_event_cancer.genomicFeatureCancer,
            tier=old_report_event_cancer.tier,
            reportEventId=old_report_event_cancer.reportEventId,
        )

        if new_report_event_cancer.genomicFeatureCancer.roleInCancer not in ['oncogene', 'TSG', 'both']:
            new_report_event_cancer.genomicFeatureCancer.roleInCancer = None

        for name, term in zip(old_report_event_cancer.soNames, old_report_event_cancer.soTerms):
            new_report_event_cancer.soTerms.append(self.new_model.SoTerm(id=term, name=name))

        if new_report_event_cancer.validate(new_report_event_cancer.toJsonDict()):
            return new_report_event_cancer
        else:
            # TODO(Greg): Improve these error messages
            raise Exception('This model can not be converted: ', new_report_event_cancer.validate_parts())

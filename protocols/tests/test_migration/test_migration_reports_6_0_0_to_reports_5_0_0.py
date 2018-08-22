from protocols.migration import MigrateReports500To600
from protocols.protocol_6_1 import reports as new_model
from protocols.protocol_7_0 import reports as old_model
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_6_0_0_to_reports_5_0_0 import MigrateReports600To500
from protocols.migration.base_migration_reports_5_0_0_and_reports_6_0_0 import BaseMigrateReports500And600


class TestMigrateReports600To500(TestCaseMigration):

    def test_migrate_interpretation_request_rd(self):
        ir_rd_6 = self.get_valid_object(object_type=old_model.InterpretationRequestRD, version=self.version_7_0)
        ir_rd_5 = MigrateReports600To500().migrate_interpretation_request_rd(old_instance=ir_rd_6)
        self.assertIsInstance(ir_rd_5, new_model.InterpretationRequestRD)
        self.assertTrue(ir_rd_5.validate(ir_rd_5.toJsonDict()))

    def test_migrate_variant_attributes(self):
        small_variant = self.variant_with_type_valid_in_both_models()

        reported_variant = MigrateReports600To500().migrate_variant_cancer(old_variant=small_variant)

        self.assertEquals(reported_variant.genomicChanges, small_variant.variantAttributes.genomicChanges)
        self.assertEquals(reported_variant.cdnaChanges, small_variant.variantAttributes.cdnaChanges)

    def test_migrate_variant_identifiers(self):
        small_variant = self.variant_with_type_valid_in_both_models()

        reported_variant = MigrateReports600To500().migrate_variant_cancer(old_variant=small_variant)

        self.assertEquals(reported_variant.dbSnpId, small_variant.variantAttributes.variantIdentifiers.dbSnpId)

    def test_migrate_variant_call(self):
        small_variant = self.variant_with_type_valid_in_both_models()

        reported_variant = MigrateReports600To500().migrate_variant_cancer(old_variant=small_variant)

        original_variant_calls = small_variant.variantCalls
        new_variant_calls = reported_variant.variantCalls

        for original_call, new_call in zip(original_variant_calls, new_variant_calls):
            self.assertEquals(new_call.phaseSet, original_call.phaseGenotype.phaseSet)
            self.assertEquals(new_call.vaf, original_call.sampleVariantAlleleFrequency)

    def test_migrate_report_events(self):
        small_variant = self.variant_with_type_valid_in_both_models()

        reported_variant = MigrateReports600To500().migrate_variant_cancer(old_variant=small_variant)

        original_reports = small_variant.reportEvents
        new_reports = reported_variant.reportEvents

        for original_report, new_report in zip(original_reports, new_reports):
            self.assertEquals(MigrateReports500To600.tier_domain_map[new_report.tier], original_report.domain)

            actions = original_report.actions
            expected_action_length = sum(map(len, (actions.prognosis, actions.therapies, actions.trials)))
            self.assertEquals(len(new_report.actions), expected_action_length)

            clinical_significance = new_report.variantClassification.clinicalSignificance
            self.assertEquals(
                BaseMigrateReports500And600.clinical_signicance_map[clinical_significance],
                original_report.variantClassification.clinicalSignificance
            )

            new_types = [ge.type for ge in new_report.genomicEntities]
            old_types = [ge.type for ge in original_report.genomicEntities]
            self.assertEquals(new_types, old_types)

    def variant_with_type_valid_in_both_models(self):
        small_variant = self.get_valid_object(object_type=old_model.SmallVariant, version=self.version_7_0)
        for re in small_variant.reportEvents:
            for ge in re.genomicEntities:
                ge.type = old_model.GenomicEntityType.intergenic
        return small_variant

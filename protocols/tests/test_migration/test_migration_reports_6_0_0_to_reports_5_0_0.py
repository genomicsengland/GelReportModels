from protocols.migration import MigrateReports500To600
from protocols.protocol_6_1 import reports as new_model
from protocols.protocol_7_0 import reports as old_model
from protocols.protocol_7_0.reports import diseaseType, TissueSource
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_6_0_0_to_reports_5_0_0 import MigrateReports600To500
from protocols.migration.base_migration_reports_5_0_0_and_reports_6_0_0 import BaseMigrateReports500And600


class TestMigrateReports600To500(BaseMigrateReports500And600, TestCaseMigration):

    def test_migrate_interpretation_request_rd(self):
        ir_rd_6 = self.get_valid_object(object_type=old_model.InterpretationRequestRD, version=self.version_7_0)
        ir_rd_5 = MigrateReports600To500().migrate_interpretation_request_rd(old_instance=ir_rd_6)
        self.assertIsInstance(ir_rd_5, new_model.InterpretationRequestRD)
        self.assertTrue(ir_rd_5.validate(ir_rd_5.toJsonDict()))

    def test_migrate_variant_attributes(self):
        small_variant = self.variant_with_type_valid_in_both_models()

        reported_variant = MigrateReports600To500().migrate_variant_cancer(old_variant=small_variant)

        self.assertEqual(reported_variant.genomicChanges, small_variant.variantAttributes.genomicChanges)
        self.assertEqual(reported_variant.cdnaChanges, small_variant.variantAttributes.cdnaChanges)

        va_6 = self.get_valid_object(
            object_type=old_model.VariantAttributes, version=self.version_7_0, fill_nullables=fill_nullables,
        )
        va_5 = MigrateReports600To500().migrate_variant_attributes(old_variant_attributes=va_6)
        self.assertIsInstance(va_5, new_model.VariantAttributes)
        self.assertTrue(va_5.validate(va_5.toJsonDict()))

    def test_migrate_variant_attributes_no_nullables(self):
        self.test_migrate_variant_attributes(fill_nullables=False)

    def test_migrate_variant_identifiers(self):
        small_variant = self.variant_with_type_valid_in_both_models()

        reported_variant = MigrateReports600To500().migrate_variant_cancer(old_variant=small_variant)

        self.assertEqual(reported_variant.dbSnpId, small_variant.variantAttributes.variantIdentifiers.dbSnpId)

    def test_migrate_variant_call(self):
        small_variant = self.variant_with_type_valid_in_both_models()

        reported_variant = MigrateReports600To500().migrate_variant_cancer(old_variant=small_variant)

        original_variant_calls = small_variant.variantCalls
        new_variant_calls = reported_variant.variantCalls

        for original_call, new_call in zip(original_variant_calls, new_variant_calls):
            self.assertEqual(new_call.phaseSet, original_call.phaseGenotype.phaseSet)
            self.assertEqual(new_call.vaf, original_call.sampleVariantAlleleFrequency)

        # AlleleOrigins are required for v5 so v6 can not have any nullables not filled
        vc_6 = self.get_valid_object(
            object_type=old_model.VariantCall, version=self.version_7_0, fill_nullables=True,
        )
        vc_5 = MigrateReports600To500().migrate_variant_call(old_call=vc_6)
        self.assertIsInstance(vc_5, new_model.VariantCall)
        self.assertTrue(vc_5.validate(vc_5.toJsonDict()))
        self.assertEqual(vc_5.phaseSet, vc_6.phaseGenotype.phaseSet)
        self.assertEqual(vc_5.vaf, vc_6.sampleVariantAlleleFrequency)

    def test_migrate_report_events(self):
        small_variant = self.variant_with_type_valid_in_both_models()

        reported_variant = MigrateReports600To500().migrate_variant_cancer(old_variant=small_variant)

        original_reports = small_variant.reportEvents
        new_reports = reported_variant.reportEvents

        for original_report, new_report in zip(original_reports, new_reports):
            self.assertEqual(MigrateReports500To600.tier_domain_map[new_report.tier], original_report.domain)

            actions = original_report.actions
            expected_action_length = sum(map(len, (actions.prognosis, actions.therapies, actions.trials)))
            self.assertEqual(len(new_report.actions), expected_action_length)

            clinical_significance = new_report.variantClassification.clinicalSignificance
            self.assertEqual(
                BaseMigrateReports500And600.clinical_signicance_map[clinical_significance],
                original_report.variantClassification.clinicalSignificance
            )

            new_types = [ge.type for ge in new_report.genomicEntities]
            old_types = [ge.type for ge in original_report.genomicEntities]
            self.assertEqual(new_types, old_types)

    def variant_with_type_valid_in_both_models(self):
        small_variant = self.get_valid_object(object_type=old_model.SmallVariant, version=self.version_7_0)
        for re in small_variant.reportEvents:
            for ge in re.genomicEntities:
                ge.type = old_model.GenomicEntityType.intergenic
        return small_variant
    
    def test_migration_of_new_enum_values_get_set_to_none(self):
        ir_6 = self.get_valid_object(object_type=old_model.CancerInterpretationRequest, version=self.version_7_0)
        samples = ir_6.cancerParticipant.tumourSamples
        for sample in samples:
            sample.diseaseType = diseaseType.ENDOCRINE
            sample.tissueSource = TissueSource.NOT_SPECIFIED

        ir_5 = MigrateReports600To500().migrate_interpretation_request_cancer(old_instance=ir_6)

        self.assertIsInstance(ir_5, new_model.CancerInterpretationRequest)
        self.assertTrue(ir_5.validate(ir_5.toJsonDict()))

        samples = ir_5.cancerParticipant.tumourSamples
        for sample in samples:
            self.assertIsNone(sample.diseaseType)
            self.assertIsNone(sample.tissueSource)

    def test_migrate_interpreted_genome_to_interpreted_genome_rd(self):
        # Small Variants are required to migrate from InterpretedGenome version 6 to InterpretedGenomeRD version 5 as
        # Reported Variants are required in v5 so nullables must be filled
        ig_6 = self.get_valid_object(
            object_type=old_model.InterpretedGenome, version=self.version_7_0, fill_nullables=True,
        )
        ig_rd_5 = MigrateReports600To500().migrate_interpreted_genome_to_interpreted_genome_rd(old_instance=ig_6)
        self.assertIsInstance(ig_rd_5, new_model.InterpretedGenomeRD)
        self.assertTrue(ig_rd_5.validate(ig_rd_5.toJsonDict()))

    def test_migrate_small_variant_to_reported_variant(self):
        # Can not reverse migrate a v6 SmallVariant to a v5 ReportedVariant if variantAttributes is None as
        # alleleOrigins is a required field in v5 ReportedVariant so nullables must be filled
        sv_6 = self.get_valid_object(
            object_type=old_model.SmallVariant, version=self.version_7_0, fill_nullables=True,
        )
        rv_5 = MigrateReports600To500().migrate_small_variant_to_reported_variant(small_variant=sv_6)
        self.assertIsInstance(rv_5, new_model.ReportedVariant)
        self.assertTrue(rv_5.validate(rv_5.toJsonDict()))

        for af in rv_5.alleleFrequencies:
            self.assertIsInstance(af, new_model.AlleleFrequency)

    def test_migrate_variant_attributes(self, fill_nullables=True):
        va_6 = self.get_valid_object(
            object_type=old_model.VariantAttributes, version=self.version_7_0, fill_nullables=fill_nullables,
        )
        va_5 = MigrateReports600To500().migrate_variant_attributes(old_variant_attributes=va_6)
        self.assertIsInstance(va_5, new_model.VariantAttributes)
        self.assertTrue(va_5.validate(va_5.toJsonDict()))

    def test_migrate_variant_attributes_no_nullables(self):
        self.test_migrate_variant_attributes(fill_nullables=False)

    def test_migrate_variant_call(self):
        # AlleleOrigins are required for v5 so v6 can not have any nullables not filled
        vc_6 = self.get_valid_object(
            object_type=old_model.VariantCall, version=self.version_7_0, fill_nullables=True,
        )
        vc_5 = MigrateReports600To500().migrate_variant_call(old_call=vc_6)
        self.assertIsInstance(vc_5, new_model.VariantCall)
        self.assertTrue(vc_5.validate(vc_5.toJsonDict()))
        self.assertEqual(vc_5.phaseSet, vc_6.phaseGenotype.phaseSet)
        self.assertEqual(vc_5.vaf, vc_6.sampleVariantAlleleFrequency)

    def test_migrate_report_event(self):
        # Can not reverse migrate v6 Report Event if phenotypes does not have nonStandardPhenotype populated as v5
        # phenotypes is required, so nullables must be filled
        re_6 = self.get_valid_object(
            object_type=old_model.ReportEvent, version=self.version_7_0, fill_nullables=True,
        )
        re_5 = MigrateReports600To500().migrate_report_event(old_event=re_6)
        self.assertIsInstance(re_5, new_model.ReportEvent)
        self.assertTrue(re_5.validate(re_5.toJsonDict()))

        for vc in re_5.variantConsequences:
            self.assertIsInstance(vc, new_model.VariantConsequence)
        self.assertIsInstance(re_5.variantClassification, new_model.VariantClassification)

    def test_migrate_interpreted_genome_to_interpreted_genome_rd(self):
        # Small Variants are required to migrate from InterpretedGenome version 6 to InterpretedGenomeRD version 5 as
        # Reported Variants are required in v5 so nullables must be filled
        ig_6 = self.get_valid_object(
            object_type=old_model.InterpretedGenome, version=self.version_7_0, fill_nullables=True,
        )
        ig_rd_5 = MigrateReports600To500().migrate_interpreted_genome_to_interpreted_genome_rd(old_instance=ig_6)
        self.assertIsInstance(ig_rd_5, new_model.InterpretedGenomeRD)
        self.assertTrue(ig_rd_5.validate(ig_rd_5.toJsonDict()))

    def test_migrate_small_variant_to_reported_variant(self):
        # Can not reverse migrate a v6 SmallVariant to a v5 ReportedVariant if variantAttributes is None as
        # alleleOrigins is a required field in v5 ReportedVariant so nullables must be filled
        sv_6 = self.get_valid_object(
            object_type=old_model.SmallVariant, version=self.version_7_0, fill_nullables=True,
        )
        rv_5 = MigrateReports600To500().migrate_small_variant_to_reported_variant(small_variant=sv_6)
        self.assertIsInstance(rv_5, new_model.ReportedVariant)
        self.assertTrue(rv_5.validate(rv_5.toJsonDict()))

        for af in rv_5.alleleFrequencies:
            self.assertIsInstance(af, new_model.AlleleFrequency)

    def test_migrate_report_event(self):
        # Can not reverse migrate v6 Report Event if phenotypes does not have nonStandardPhenotype populated as v5
        # phenotypes is required, so nullables must be filled
        re_6 = self.get_valid_object(
            object_type=old_model.ReportEvent, version=self.version_7_0, fill_nullables=True,
        )
        re_5 = MigrateReports600To500().migrate_report_event(old_event=re_6)
        self.assertIsInstance(re_5, new_model.ReportEvent)
        self.assertTrue(re_5.validate(re_5.toJsonDict()))

        for vc in re_5.variantConsequences:
            self.assertIsInstance(vc, new_model.VariantConsequence)
        self.assertIsInstance(re_5.variantClassification, new_model.VariantClassification)

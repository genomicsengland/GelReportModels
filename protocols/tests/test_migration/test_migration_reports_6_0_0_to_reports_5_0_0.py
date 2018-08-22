from protocols import reports_6_0_0
from protocols import reports_5_0_0
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_6_0_0_to_reports_5_0_0 import MigrateReports600To500


class TestMigrateReports600To500(TestCaseMigration):

    old_model = reports_6_0_0
    new_model = reports_5_0_0

    def test_migrate_interpretation_request_rd(self):
        ir_rd_6 = self.get_valid_object(object_type=self.old_model.InterpretationRequestRD, version=self.version_7_0)
        ir_rd_5 = MigrateReports600To500().migrate_interpretation_request_rd(old_instance=ir_rd_6)
        self.assertIsInstance(ir_rd_5, self.new_model.InterpretationRequestRD)
        self.assertTrue(ir_rd_5.validate(ir_rd_5.toJsonDict()))

    def test_migrate_interpreted_genome_to_interpreted_genome_rd(self):
        # Small Variants are required to migrate from InterpretedGenome version 6 to InterpretedGenomeRD version 5 as
        # Reported Variants are required in v5 so nullables must be filled
        ig_6 = self.get_valid_object(
            object_type=self.old_model.InterpretedGenome, version=self.version_7_0, fill_nullables=True,
        )
        ig_rd_5 = MigrateReports600To500().migrate_interpreted_genome_to_interpreted_genome_rd(old_instance=ig_6)
        self.assertIsInstance(ig_rd_5, self.new_model.InterpretedGenomeRD)
        self.assertTrue(ig_rd_5.validate(ig_rd_5.toJsonDict()))

    def test_migrate_small_variant_to_reported_variant(self):
        # Can not reverse migrate a v6 SmallVariant to a v5 ReportedVariant if variantAttributes is None as
        # alleleOrigins is a required field in v5 ReportedVariant so nullables must be filled
        sv_6 = self.get_valid_object(
            object_type=self.old_model.SmallVariant, version=self.version_7_0, fill_nullables=True,
        )
        rv_5 = MigrateReports600To500().migrate_small_variant_to_reported_variant(small_variant=sv_6)
        self.assertIsInstance(rv_5, self.new_model.ReportedVariant)
        self.assertTrue(rv_5.validate(rv_5.toJsonDict()))

        for af in rv_5.alleleFrequencies:
            self.assertIsInstance(af, self.new_model.AlleleFrequency)

    def test_migrate_variant_attributes(self, fill_nullables=True):
        va_6 = self.get_valid_object(
            object_type=self.old_model.VariantAttributes, version=self.version_7_0, fill_nullables=fill_nullables,
        )
        va_5 = MigrateReports600To500().migrate_variant_attributes(old_variant_attributes=va_6)
        self.assertIsInstance(va_5, self.new_model.VariantAttributes)
        self.assertTrue(va_5.validate(va_5.toJsonDict()))

    def test_migrate_variant_attributes_no_nullables(self):
        self.test_migrate_variant_attributes(fill_nullables=False)

    def test_migrate_variant_call(self):
        # AlleleOrigins are required for v5 so v6 can not have any nullables not filled
        vc_6 = self.get_valid_object(
            object_type=self.old_model.VariantCall, version=self.version_7_0, fill_nullables=True,
        )
        vc_5 = MigrateReports600To500().migrate_variant_call(old_call=vc_6)
        self.assertIsInstance(vc_5, self.new_model.VariantCall)
        self.assertTrue(vc_5.validate(vc_5.toJsonDict()))
        self.assertEqual(vc_5.phaseSet, vc_6.phaseGenotype.phaseSet)
        self.assertEqual(vc_5.vaf, vc_6.sampleVariantAlleleFrequency)

    def test_migrate_report_event(self):
        # Can not reverse migrate v6 Report Event if phenotypes does not have nonStandardPhenotype populated as v5
        # phenotypes is required, so nullables must be filled
        re_6 = self.get_valid_object(
            object_type=self.old_model.ReportEvent, version=self.version_7_0, fill_nullables=True,
        )
        re_5 = MigrateReports600To500().migrate_report_event(old_event=re_6)
        self.assertIsInstance(re_5, self.new_model.ReportEvent)
        self.assertTrue(re_5.validate(re_5.toJsonDict()))

        for vc in re_5.variantConsequences:
            self.assertIsInstance(vc, self.new_model.VariantConsequence)
        self.assertIsInstance(re_5.variantClassification, self.new_model.VariantClassification)

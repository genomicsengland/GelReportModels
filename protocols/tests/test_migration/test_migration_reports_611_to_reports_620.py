from protocols import reports_6_1_1, reports_6_2_0
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_611_to_reports_620 import MigrateReports611To620


class TestMigrateReport611To620(TestCaseMigration):
    old_model = reports_6_1_1
    new_model = reports_6_2_0

    def test_migrate_variant_interpretation_log(self):
        vil_6_1_1 = self.get_valid_object(object_type=self.old_model.VariantInterpretationLog,
                                           version=self.version_7_7,
                                           fill_nullables=True
                                           )
        # Check we have at least one ACMG evidence (should do because nulls are filled)
        self.assertGreater(len(vil_6_1_1.variantClassification.acmgVariantClassification.acmgEvidences), 0)
        self.assertGreater(len(vil_6_1_1.comments), 0)
        # Set type to "bening" enum
        for acmg_evidence in vil_6_1_1.variantClassification.acmgVariantClassification.acmgEvidences:
            acmg_evidence.type = "bening"
        # Test we haven't broken the model in previous step
        self.assertTrue(self.old_model.VariantInterpretationLog.validate(vil_6_1_1.toJsonDict()))
        # Migrate
        vil_6_2_0 = MigrateReports611To620().migrate_variant_interpretation_log(old_instance=vil_6_1_1)
        self.assertIsInstance(vil_6_2_0, self.new_model.VariantInterpretationLog)
        self.assertTrue(self.new_model.VariantInterpretationLog.validate(vil_6_2_0.toJsonDict()))
        # Test that the spelling has corrected from "bening" to "benign"
        for acmg_evidence in vil_6_2_0.variantClassification.acmgVariantClassification.acmgEvidences:
            self.assertIs(acmg_evidence.type, "benign")
        # Test that comments have migrated over
        for index, comment in enumerate(vil_6_1_1.comments):
            self.assertEqual(vil_6_2_0.comments[index].comment, comment)
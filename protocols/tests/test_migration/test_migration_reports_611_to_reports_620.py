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
        # Check we have two ACMG evidences (should do because factory fills array with 2 elements by default)
        self.assertGreater(len(vil_6_1_1.variantClassification.acmgVariantClassification.acmgEvidences), 1)
        # Check we have at least one comment
        self.assertGreater(len(vil_6_1_1.comments), 0)
        acmg_evidences_6_1_1 = vil_6_1_1.variantClassification.acmgVariantClassification.acmgEvidences
        # Set type to "bening" enum
        for acmg_evidence in acmg_evidences_6_1_1:
            acmg_evidence.type = "bening"
        acmg_evidences_6_1_1[0].activationStrength = None
        acmg_evidences_6_1_1[1].weight = "strong"
        acmg_evidences_6_1_1[1].weight = "supporting"
        # Test we haven't broken the model in previous step
        self.assertTrue(self.old_model.VariantInterpretationLog.validate(vil_6_1_1.toJsonDict()))
        # Migrate
        vil_6_2_0 = MigrateReports611To620().migrate_variant_interpretation_log(old_instance=vil_6_1_1)
        self.assertIsInstance(vil_6_2_0, self.new_model.VariantInterpretationLog)
        self.assertTrue(self.new_model.VariantInterpretationLog.validate(vil_6_2_0.toJsonDict()))
        acmg_evidences_6_2_0 = vil_6_2_0.variantClassification.acmgVariantClassification.acmgEvidences
        # Test that the spelling has corrected from "bening" to "benign"
        for acmg_evidence in acmg_evidences_6_2_0:
            self.assertIs(acmg_evidence.type, "benign")
        # Test that comments have migrated over
        for index, comment in enumerate(vil_6_1_1.comments):
            self.assertEqual(vil_6_2_0.comments[index].comment, comment)
        # For evidence that had no activation strength, it should have taken value from weight field
        self.assertEqual(acmg_evidences_6_2_0[0].activationStrength, acmg_evidences_6_1_1[0].weight)
        # For evidence that had activation strength, this should have copied accross
        self.assertEqual(acmg_evidences_6_2_0[1].activationStrength, acmg_evidences_6_1_1[1].activationStrength)
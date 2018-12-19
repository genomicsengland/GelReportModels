from protocols.migration.migration_reports_601_to_reports_600 import MigrateReports601To600
from protocols.protocol_7_0 import reports as new_model
from protocols.protocol_7_2 import reports as old_model
from protocols.tests.test_migration.base_test_migration import TestCaseMigration


class TestMigrateReports601To600(TestCaseMigration):

    def test_migrate_interpretation_request_rd(self, fill_nullables=True):
        ir_rd_601 = self.get_valid_object(object_type=old_model.InterpretationRequestRD, version=self.version_7_2,
                                          fill_nullables=fill_nullables)
        ir_rd_601.interpretationFlags.append(old_model.InterpretationFlag(
            interpretationFlag=old_model.InterpretationFlags.cnv_calls_assumed_xx_karyo
        ))
        ir_rd_600 = MigrateReports601To600().migrate_interpretation_request_rd(old_instance=ir_rd_601)
        self.assertIsInstance(ir_rd_600, new_model.InterpretationRequestRD)
        self.assertTrue(ir_rd_600.validate(ir_rd_600.toJsonDict()))
        self.assertIn(old_model.InterpretationFlags.cnv_calls_assumed_xx_karyo, [interpretation_flag.additionalDescription
                                                                                 for interpretation_flag in ir_rd_600.interpretationFlags
                                                                                 ])

    def test_migrate_exit_questionnaire_rd(self, fill_nullables=True):
        eq_rd_601 = self.get_valid_object(object_type=old_model.RareDiseaseExitQuestionnaire, version=self.version_7_2,
                                          fill_nullables=fill_nullables)

        eq_rd_600 = MigrateReports601To600().migrate_exit_questionnaire_rd(old_instance=eq_rd_601)
        self.assertIsInstance(eq_rd_600, new_model.RareDiseaseExitQuestionnaire)
        self.assertTrue(eq_rd_600.validate(eq_rd_600.toJsonDict()))

        eq_rd_601.variantGroupLevelQuestions = None
        eq_rd_600 = MigrateReports601To600().migrate_exit_questionnaire_rd(old_instance=eq_rd_601)
        self.assertIsInstance(eq_rd_600, new_model.RareDiseaseExitQuestionnaire)
        self.assertTrue(eq_rd_600.validate(eq_rd_600.toJsonDict()))

    def test_migrate_exit_questionnaire_cancer(self, fill_nullables=True):
        eq_cancer_601 = self.get_valid_object(object_type=old_model.CancerExitQuestionnaire, version=self.version_7_2,
                                           fill_nullables=fill_nullables)

        eq_cancer_600 = MigrateReports601To600().migrate_exit_questionnaire_cancer(old_instance=eq_cancer_601)
        self.assertIsInstance(eq_cancer_600, new_model.CancerExitQuestionnaire)
        self.assertTrue(eq_cancer_600.validate(eq_cancer_600.toJsonDict()))

        eq_cancer_601.variantGroupLevelQuestions = None
        eq_cancer_600 = MigrateReports601To600().migrate_exit_questionnaire_cancer(old_instance=eq_cancer_601)
        self.assertIsInstance(eq_cancer_600, new_model.CancerExitQuestionnaire)
        self.assertTrue(eq_cancer_600.validate(eq_cancer_600.toJsonDict()))

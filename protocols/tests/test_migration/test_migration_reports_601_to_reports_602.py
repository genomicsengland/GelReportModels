from protocols import reports_6_0_1, reports_6_0_2
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_601_to_reports_602 import MigrateReports601To602


class TestMigrateReport601To602(TestCaseMigration):
    old_model = reports_6_0_1
    new_model = reports_6_0_2

    def test_migrate_interpretation_request_rd(self):
        i_rd_6_0_1 = self.get_valid_object(object_type=self.old_model.InterpretationRequestRD,
                                           version=self.version_7_2,
                                           fill_nullables=True
                                           )
        i_rd_6_0_2 = MigrateReports601To602().migrate_interpretation_request_rd(old_instance=i_rd_6_0_1)
        self.assertIsInstance(i_rd_6_0_2, self.new_model.InterpretationRequestRD)
        self.assertTrue(self.new_model.InterpretationRequestRD.validate(i_rd_6_0_2.toJsonDict()))
        self.assertIsInstance(i_rd_6_0_2.pedigree.members[0].samples[0].labSampleId, str)

    def test_migrate_interpretation_request_cancer(self):
        cancer_6_0_1 = self.get_valid_object(object_type=self.old_model.CancerInterpretationRequest,
                                             version=self.version_7_2,
                                             fill_nullables=True
                                             )
        cancer_6_0_2 = MigrateReports601To602().migrate_interpretation_request_cancer(old_instance=cancer_6_0_1)
        self.assertIsInstance(cancer_6_0_2, self.new_model.CancerInterpretationRequest)
        self.assertTrue(self.new_model.CancerInterpretationRequest.validate(cancer_6_0_2.toJsonDict()))
        self.assertIsInstance(cancer_6_0_2.cancerParticipant.tumourSamples[0].labSampleId, str)
        self.assertIsInstance(cancer_6_0_2.cancerParticipant.germlineSamples[0].labSampleId, str)
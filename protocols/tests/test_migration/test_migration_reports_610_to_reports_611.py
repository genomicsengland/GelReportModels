from protocols import reports_6_1_0, reports_6_1_1
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_610_to_reports_611 import MigrateReports610To611


class TestMigrateReport610To611(TestCaseMigration):
    old_model = reports_6_1_0
    new_model = reports_6_1_1

    def test_migrate_interpretation_request_rd(self):
        i_rd_6_1_0 = self.get_valid_object(object_type=self.old_model.InterpretationRequestRD,
                                           version=self.version_7_3,
                                           fill_nullables=True
                                           )
        i_rd_6_1_1 = MigrateReports610To611().migrate_interpretation_request_rd(old_instance=i_rd_6_1_0)
        self.assertIsInstance(i_rd_6_1_1, self.new_model.InterpretationRequestRD)
        self.assertTrue(self.new_model.InterpretationRequestRD.validate(i_rd_6_1_1.toJsonDict()))
        self.assertIsInstance(i_rd_6_1_1.pedigree.members[0].samples[0].labSampleId, str)

    def test_migrate_interpretation_request_cancer(self):
        cancer_6_1_0 = self.get_valid_object(object_type=self.old_model.CancerInterpretationRequest,
                                             version=self.version_7_3,
                                             fill_nullables=True
                                             )
        cancer_6_1_1 = MigrateReports610To611().migrate_interpretation_request_cancer(old_instance=cancer_6_1_0)
        self.assertIsInstance(cancer_6_1_1, self.new_model.CancerInterpretationRequest)
        self.assertTrue(self.new_model.CancerInterpretationRequest.validate(cancer_6_1_1.toJsonDict()))
        self.assertIsInstance(cancer_6_1_1.cancerParticipant.tumourSamples[0].labSampleId, str)
        self.assertIsInstance(cancer_6_1_1.cancerParticipant.germlineSamples[0].labSampleId, str)
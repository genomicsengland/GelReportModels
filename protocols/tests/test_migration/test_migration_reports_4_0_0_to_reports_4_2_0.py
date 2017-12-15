from unittest import TestCase

from protocols import reports_4_0_0
from protocols import reports_4_2_0
from protocols.migration import MigrateReports400To420
from protocols.util.dependency_manager import VERSION_400
from protocols.util.dependency_manager import VERSION_500
from protocols.util.factories.avro_factory import GenericFactoryAvro


class TestMigrateReports4To420(TestCase):

    old_model = reports_4_0_0
    new_model = reports_4_2_0

    def test_migrate_cancer_clinical_report(self):
        cr_c_400 = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportCancer, VERSION_400, fill_nullables=True
        ).create()
        self.assertTrue(cr_c_400.validate(cr_c_400.toJsonDict()))

        cr_c_420 = GenericFactoryAvro.get_factory_avro(
            self.new_model.ClinicalReportCancer, VERSION_500
        ).create()
        self.assertTrue(cr_c_420.validate(cr_c_420.toJsonDict()))

        migrated_cir_420 = MigrateReports400To420().migrate_cancer_clinical_report(
            cancer_clinical_report=cr_c_400, sample_id='test_sample_id'
        )

        self.assertTrue(migrated_cir_420.validate(migrated_cir_420.toJsonDict()))

        for cv_400, cv_420 in zip(cr_c_400.candidateVariants, migrated_cir_420.candidateVariants):
            self.assertEqual(cv_400.reportedVariantCancer.reference, cv_420.reference)
            self.assertEqual(cv_400.reportedVariantCancer.alternate, cv_420.alternate)
            self.assertEqual(cv_400.reportedVariantCancer.position, cv_420.position)

    def test_migrate_cir_400_to_420(self):

        cir_400 = GenericFactoryAvro.get_factory_avro(
            self.old_model.CancerInterpretationRequest, VERSION_400
        )()

        cir_400.cancerParticipant.LDPCode = 'test_LDP_code_migrate_cir_400_to_420'
        cir_400.tieredVariants[0].reportedVariantCancer.reportEvents[0].actions = [self.old_model.Actions()]
        cir_400.tieredVariants[0].reportedVariantCancer.reportEvents[0].actions[0].actionType = self.old_model.ActionType.diagnosis
        cir_400.tieredVariants[0].reportedVariantCancer.reportEvents[0].actions[0].variantActionable = False

        self.assertIsInstance(cir_400, self.old_model.CancerInterpretationRequest)
        self.assertTrue(cir_400.validate(cir_400.toJsonDict()))

        migrated_cir = MigrateReports400To420().migrate_cancer_interpretation_request(
            cancer_interpretation_request=cir_400,
            sample_id="sample1"
        )
        self.assertIsInstance(migrated_cir, self.new_model.CancerInterpretationRequest)
        self.assertTrue(migrated_cir.validate(migrated_cir.toJsonDict()))

        self.assertEqual(
            migrated_cir.tieredVariants[0].reportEvents[0].actions[0].actionType,
            self.new_model.ActionType.diagnosis
        )

        cir_400.tieredVariants[0].reportedVariantCancer.reportEvents[0].actions[0].actionType = "Therapeutic (colorectal ca)"
        self.assertIsInstance(cir_400, self.old_model.CancerInterpretationRequest)
        self.assertTrue(cir_400.validate(cir_400.toJsonDict()))
        migrated_cir = MigrateReports400To420().migrate_cancer_interpretation_request(
            cancer_interpretation_request=cir_400,
            sample_id="sample1"
        )
        self.assertIsInstance(migrated_cir, self.new_model.CancerInterpretationRequest)
        self.assertTrue(migrated_cir.validate(migrated_cir.toJsonDict()))
        self.assertEqual(
            migrated_cir.tieredVariants[0].reportEvents[0].actions[0].actionType,
            self.new_model.ActionType.therapeutic
        )
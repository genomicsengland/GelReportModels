from unittest import TestCase

import factory
from protocols import reports_4_0_0
from protocols import reports_5_0_0
from protocols.migration.migration_reports_4_0_0_to_reports_5_0_0 import MigrateReports400To500
from protocols.util.dependency_manager import VERSION_400
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.util.factories.avro_factory import FactoryAvro


class ActionFactory(FactoryAvro):
    class Meta:
        model = reports_4_0_0.Actions

    _version = VERSION_400

    actionType = factory.fuzzy.FuzzyChoice(['therapy', 'therapeutic', 'prognosis', 'diagnosis'])
    status = factory.fuzzy.FuzzyChoice(['clinical', 'pre-clinical'])


class TestMigrateReports4To500(TestCase):

    old_model = reports_4_0_0
    new_model = reports_5_0_0

    def test_migrate_cancer_clinical_report(self):

        fill_nullables = True

        GenericFactoryAvro.register_factory(
            reports_4_0_0.Actions, ActionFactory, VERSION_400, fill_nullables=fill_nullables)

        cr_c_400 = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportCancer, VERSION_400, fill_nullables=fill_nullables
        ).create(interpretationRequestVersion='1')
        self.assertTrue(cr_c_400.validate(cr_c_400.toJsonDict()))

        migrated_cir_500 = MigrateReports400To500().migrate_cancer_clinical_report(
            cr_c_400, assembly='grch38', participant_id="noone", sample_id='some'
        )

        self.assertTrue(migrated_cir_500.validate(migrated_cir_500.toJsonDict()))

        # for cv_400, cv_420 in zip(cr_c_400.candidateVariants, migrated_cir_500.variants):
        #     self.assertEqual(cv_400.reportedVariantCancer.reference, cv_420.reference)
        #     self.assertEqual(cv_400.reportedVariantCancer.alternate, cv_420.alternate)
        #     self.assertEqual(cv_400.reportedVariantCancer.position, cv_420.position)

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

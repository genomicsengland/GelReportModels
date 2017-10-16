from unittest import TestCase

from protocols import reports_4_0_0
from protocols import reports_4_2_0
from protocols import participant_1_0_4
from protocols import participant_1_0_0
from protocols.migration import MigrateReports420To400
from protocols.migration import MigrationParticipants104To100
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.util.dependency_manager import VERSION_430


class TestMigrateReports420To4(TestCase):

    old_model = reports_4_2_0
    new_model = reports_4_0_0

    def test_migrate_cir_420_to_400(self):

        cir_420 = GenericFactoryAvro.get_factory_avro(reports_4_2_0.CancerInterpretationRequest, VERSION_430)()

        # Check cir_420 is a valid reports_4_2_0 CancerInterpretationRequest object
        self.assertIsInstance(cir_420, self.old_model.CancerInterpretationRequest)
        self.assertTrue(cir_420.validate(jsonDict=cir_420.toJsonDict()))

        migrated_object = MigrateReports420To400().migrate_cancer_interpretation_request(
            cancer_interpretation_request=cir_420
        )

        # Check migrated_object is a valid reports_4_0_0 CancerInterpretationRequest object
        self.assertIsInstance(migrated_object, self.new_model.CancerInterpretationRequest)
        self.assertTrue(migrated_object.validate(jsonDict=migrated_object.toJsonDict()))


class TestMigrationParticipants104To100(TestCase):

    old_model = participant_1_0_4
    new_model = participant_1_0_0

    def test_migrate_tumour_sample(self):

        old_tumour_sample = GenericFactoryAvro.get_factory_avro(self.old_model.TumourSample, VERSION_430)()
        self.assertIsInstance(old_tumour_sample, self.old_model.TumourSample)
        self.assertTrue(old_tumour_sample.validate(old_tumour_sample.toJsonDict()))
        migrated_sample = MigrationParticipants104To100().migrate_tumour_sample(
            tumour_sample=old_tumour_sample
        )

        self.assertIsInstance(migrated_sample, self.new_model.TumourSample)
        self.assertTrue(migrated_sample.validate(migrated_sample.toJsonDict()))
        self.assertEqual(migrated_sample.sampleId, old_tumour_sample.sampleId)
        self.assertEqual(migrated_sample.labSampleId, old_tumour_sample.labSampleId)
        try:
            tumourId = int(old_tumour_sample.tumourId)
        except ValueError:
            tumourId = old_tumour_sample.labSampleId
        self.assertEqual(migrated_sample.tumourId, tumourId)
        self.assertEqual(migrated_sample.tumourContent, old_tumour_sample.tumourContent)
        self.assertEqual(migrated_sample.source, old_tumour_sample.source)
        self.assertEqual(migrated_sample.preparationMethod, old_tumour_sample.preparationMethod)
        self.assertEqual(migrated_sample.tissueSource, old_tumour_sample.tissueSource)
        self.assertEqual(migrated_sample.product, old_tumour_sample.product)
        self.assertEqual(migrated_sample.tumourType, old_tumour_sample.diseaseType)
        self.assertEqual(migrated_sample.tumourSubType, old_tumour_sample.diseaseSubType)
        self.assertEqual(migrated_sample.phase, old_tumour_sample.tumourType)

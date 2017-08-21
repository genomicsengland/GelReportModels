from unittest import TestCase

from protocols import participant_1_0_0
from protocols import participant_1_0_4_SNAPSHOT
from protocols.util import get_valid_cancer_participant_1_0_4_SNAPSHOT
from protocols.migration import MigrationParticipants104SNAPSHOTTo100


class TestMigrationParticipants104SNAPSHOTTo100(TestCase):

    old_model = participant_1_0_4_SNAPSHOT
    new_model = participant_1_0_0

    def test_migrate_tumour_sample(self):

        # these should be migrated with the same names
        test_sample_id = '1'
        test_lab_sample_id = 1
        test_tumour_id = '2'
        test_tumour_content = self.old_model.TumourContent.High
        test_sample_source = self.old_model.SampleSource.FIBROBLAST
        test_preparation_method = self.old_model.PreparationMethod.FF
        test_tissue_source = self.old_model.TissueSource.BMA_TUMOUR_SORTED_CELLS
        test_product = self.old_model.Product.DNA

        # this should equal new_sample.tumourType
        test_disease_type = self.old_model.diseaseType.ADULT_GLIOMA

        # this should equal new_sample.tumourSubType
        test_disease_subtype = 'test_disease_subtype'

        # this should equal new_sample.phase
        test_tumour_type = self.old_model.TumourType.METASTASES

        old_tumour_sample = self.old_model.TumourSample(
            sampleId=test_sample_id,
            labSampleId=test_lab_sample_id,
            tumourId=test_tumour_id,
            diseaseType=test_disease_type,
            diseaseSubType=test_disease_subtype,
            tumourType=test_tumour_type,
            tumourContent=test_tumour_content,
            source=test_sample_source,
            preparationMethod=test_preparation_method,
            tissueSource=test_tissue_source,
            product=test_product,
        )

        self.assertIsInstance(old_tumour_sample, self.old_model.TumourSample)
        self.assertTrue(old_tumour_sample.validate(old_tumour_sample.toJsonDict()))

        migrated_sample = MigrationParticipants104SNAPSHOTTo100().migrate_tumour_sample(
            tumour_sample=old_tumour_sample
        )

        self.assertIsInstance(migrated_sample, self.new_model.TumourSample)
        self.assertTrue(migrated_sample.validate(migrated_sample.toJsonDict()))

        self.assertEqual(migrated_sample.sampleId, test_sample_id)
        self.assertEqual(migrated_sample.labSampleId, test_lab_sample_id)
        self.assertEqual(migrated_sample.tumourId, int(test_tumour_id))
        self.assertEqual(migrated_sample.tumourContent, test_tumour_content)
        self.assertEqual(migrated_sample.source, test_sample_source)
        self.assertEqual(migrated_sample.preparationMethod, test_preparation_method)
        self.assertEqual(migrated_sample.tissueSource, test_tissue_source)
        self.assertEqual(migrated_sample.product, test_product)

        self.assertEqual(migrated_sample.tumourType, test_disease_type)

        self.assertEqual(migrated_sample.tumourSubType, test_disease_subtype)

        self.assertEqual(migrated_sample.phase, test_tumour_type)


class TestMigrateReports3ToParticipant1(TestCase):

    old_model = participant_1_0_4_SNAPSHOT
    new_model = participant_1_0_0

    def test_migrate_cancer_participant(self):

        old_participant = get_valid_cancer_participant_1_0_4_SNAPSHOT()

        # Check old_participant is a valid participants_1_0_4_SNAPSHOT CancerParticipant object
        self.assertTrue(isinstance(old_participant, self.old_model.CancerParticipant))
        self.assertTrue(old_participant.validate(jsonDict=old_participant.toJsonDict()))

        # # Perform the migration of old_participant from participants_1_0_4_SNAPSHOT to participants_1_0_0
        migrated_participant = MigrationParticipants104SNAPSHOTTo100().migrate_cancer_participant(old_participant)

        # # Check migrated_participant is a valid participant_1_0_0 CancerParticipant object
        self.assertTrue(isinstance(migrated_participant, self.new_model.CancerParticipant))
        self.assertTrue(migrated_participant.validate(jsonDict=migrated_participant.toJsonDict()))

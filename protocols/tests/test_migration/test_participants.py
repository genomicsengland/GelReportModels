from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols import participant_1_0_0
from protocols import participant_1_0_3
from protocols import participant_1_1_0
from protocols.util.dependency_manager import VERSION_500
from protocols.util.dependency_manager import VERSION_400
from protocols.migration import MigrationParticipants100To103
from protocols.migration import MigrationParticipants103To110
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.util.factories.participant_1_0_0_factories import CancerParticipantFactory


class TestMigrationParticipants103To110(TestCaseMigration):

    old_model = participant_1_0_3
    new_model = participant_1_1_0

    def test_migrate_cancer_participant(self):

        old_participant = GenericFactoryAvro.get_factory_avro(
            clazz=participant_1_0_3.CancerParticipant, version=VERSION_500, fill_nullables=True)()
        migrated_participant = MigrationParticipants103To110().migrate_cancer_participant(old_participant)
        self.assertIsInstance(migrated_participant, self.new_model.CancerParticipant)
        self._validate(migrated_participant)

        old_participant = GenericFactoryAvro.get_factory_avro(
            clazz=participant_1_0_3.CancerParticipant, version=VERSION_500, fill_nullables=False)()
        migrated_participant = MigrationParticipants103To110().migrate_cancer_participant(old_participant)
        self.assertIsInstance(migrated_participant, self.new_model.CancerParticipant)
        self._validate(migrated_participant)

    def test_migrate_pedigree(self):

        old_pedigree = GenericFactoryAvro.get_factory_avro(
            clazz=participant_1_0_3.Pedigree, version=VERSION_500, fill_nullables=True)()
        migrated_pedigree = MigrationParticipants103To110().migrate_pedigree(old_pedigree)
        self.assertIsInstance(migrated_pedigree, self.new_model.Pedigree)
        self._validate(migrated_pedigree)

        old_pedigree = GenericFactoryAvro.get_factory_avro(
            clazz=participant_1_0_3.Pedigree, version=VERSION_500, fill_nullables=False)()
        migrated_pedigree = MigrationParticipants103To110().migrate_pedigree(old_pedigree)
        self.assertIsInstance(migrated_pedigree, self.new_model.Pedigree)
        self._validate(migrated_pedigree)


class TestMigrationParticipants100To103(TestCaseMigration):

    old_model = participant_1_0_0
    new_model = participant_1_0_3

    def test_migrate_cancer_participant(self):

        GenericFactoryAvro.register_factory(clazz=participant_1_0_0.CancerParticipant, factory=CancerParticipantFactory)
        old_participant = GenericFactoryAvro.get_factory_avro(clazz=participant_1_0_0.CancerParticipant, version=VERSION_400)()
        matched_samples = self.old_model.MatchedSamples(
            germlineSampleId='test_germline_id', tumourSampleId='test_tumour_id'
        )
        old_participant.matchedSamples = [matched_samples]
        old_participant.LDPCode = 'test_LDP_code'

        self.assertIsInstance(old_participant, self.old_model.CancerParticipant)
        self._validate(old_participant)

        migrated_participant = MigrationParticipants100To103().migrate_cancer_participant(
            old_instance=old_participant
        )

        self.assertIsInstance(migrated_participant, self.new_model.CancerParticipant)
        self._validate(migrated_participant)

        self.assertIsInstance(migrated_participant.versionControl, self.new_model.VersionControl)
        self.assertDictEqual(migrated_participant.versionControl.toJsonDict(), {"GitVersionControl": "1.0.3"})

        for germline_sample in migrated_participant.germlineSamples:
            self.assertEqual(germline_sample.LDPCode, old_participant.LDPCode)
        for tumour_sample in migrated_participant.tumourSamples:
            self.assertEqual(tumour_sample.LDPCode, old_participant.LDPCode)

        for matched_sample in migrated_participant.matchedSamples:
            self.assertIsInstance(matched_sample, self.new_model.MatchedSamples)

        for old_matched_sample, new_matched_sample in zip(old_participant.matchedSamples, migrated_participant.matchedSamples):
            self.assertDictEqual(old_matched_sample.toJsonDict(), new_matched_sample.toJsonDict())

    def test_migrate_tumour_sample(self):

        # these should be migrated with the same names
        test_sample_id = '1'
        test_lab_sample_id = 1
        test_tumour_id = 2
        test_tumour_content = self.old_model.TumourContent.High
        test_sample_source = self.old_model.SampleSource.FIBROBLAST
        test_preparation_method = self.old_model.PreparationMethod.FF
        test_tissue_source = self.old_model.TissueSource.BMA_TUMOUR_SORTED_CELLS
        test_product = self.old_model.Product.DNA

        # this should equal new_sample.diseaseType
        test_tumour_type = self.old_model.TumourType.ADULT_GLIOMA

        # this should equal new_sample.diseaseSubType
        test_tumour_subtype = 'test_tumour_subtype'

        # this should equal new_sample.tumourType
        test_phase = self.old_model.Phase.METASTASES

        old_tumour_sample = self.old_model.TumourSample(
            sampleId=test_sample_id,
            labSampleId=test_lab_sample_id,
            tumourId=test_tumour_id,
            tumourSubType=test_tumour_subtype,
            tumourType=test_tumour_type,
            tumourContent=test_tumour_content,
            source=test_sample_source,
            preparationMethod=test_preparation_method,
            tissueSource=test_tissue_source,
            product=test_product,
            phase=test_phase,
        )

        self.assertIsInstance(old_tumour_sample, self.old_model.TumourSample)
        self._validate(old_tumour_sample)

        migrated_sample = MigrationParticipants100To103()._migrate_tumour_sample(
            tumour_sample=old_tumour_sample, LDPCode='test_ldp_code'
        )

        self.assertIsInstance(migrated_sample, self.new_model.TumourSample)
        self._validate(migrated_sample)

        self.assertEqual(migrated_sample.sampleId, test_sample_id)
        self.assertEqual(migrated_sample.labSampleId, test_lab_sample_id)
        self.assertEqual(migrated_sample.tumourId, str(test_tumour_id))
        self.assertEqual(migrated_sample.tumourContent, test_tumour_content)
        self.assertEqual(migrated_sample.source, test_sample_source)
        self.assertEqual(migrated_sample.preparationMethod, test_preparation_method)
        self.assertEqual(migrated_sample.tissueSource, test_tissue_source)
        self.assertEqual(migrated_sample.product, test_product)

        self.assertEqual(migrated_sample.diseaseType, test_tumour_type)
        self.assertEqual(migrated_sample.diseaseSubType, test_tumour_subtype)
        self.assertEqual(migrated_sample.tumourType, test_phase)

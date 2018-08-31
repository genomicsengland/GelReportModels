from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.reports_3_0_0 import CancerParticipant as CancerParticipant_old
from protocols.participant_1_0_0 import CancerParticipant as CancerParticipant_new
from protocols.migration.migration_reports_300_to_participant_100 import MigrationReports3ToParticipant1
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.util.dependency_manager import VERSION_400, VERSION_300
from protocols import reports_3_0_0


class TestMigrateReports3ToParticipant1(TestCaseMigration):

    old_model = reports_3_0_0

    def test_migrate_cancer_participant(self):

        # creates a random clinical report cancer for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            CancerParticipant_old, VERSION_300, fill_nullables=True
        ).create()
        # NOTE: we enforce the field labId to follow an integer format as it is a precondition of migration
        for cancer_sample in old_instance.cancerSamples:
            cancer_sample.labId = "12345"
        # NOTE: enforces at least one tumour and one germline sample
        old_instance.cancerSamples[0].sampleType = self.old_model.SampleType.germline
        old_instance.cancerSamples[1].sampleType = self.old_model.SampleType.tumor

        self._validate(old_instance)
        self._check_non_empty_fields(old_instance)

        new_instance = MigrationReports3ToParticipant1().migrate_cancer_participant(old_instance)
        self._validate(new_instance)
        self._check_non_empty_fields(
            new_instance,
            exclusions=["clinicalSampleDateTime", "preparationMethod", "product", "primaryDiagnosisSubDisease",
                        "source", "tissueSource", "tumourContent", "tumourType"])

        old_participant = GenericFactoryAvro.get_factory_avro(CancerParticipant_old, VERSION_300)()
        new_participant = GenericFactoryAvro.get_factory_avro(CancerParticipant_new, VERSION_400)()

        for cancer_sample in old_participant.cancerSamples:
            cancer_sample.tumorType = 'lung'
            cancer_sample.tumorSubType = 'mock_subtype'
            cancer_sample.tumorContent = 'High'
            cancer_sample.labId = "1"
        old_participant.cancerSamples[0].sampleType = self.old_model.SampleType.tumor

        # Check old_participant is a valid reports_3_0_0 CancerParticipant object
        self.assertTrue(isinstance(old_participant, CancerParticipant_old))
        self._validate(old_participant)

        # Check new_participant is a valid participant_1_0_0 CancerParticipant object
        self.assertTrue(isinstance(new_participant, CancerParticipant_new))
        self._validate(new_participant)

        # Perform the migration of old_participant from reports_3_0_0 to participant_1_0_0
        migrated_participant = MigrationReports3ToParticipant1().migrate_cancer_participant(old_participant)

        # Check migrated_participant is a valid participant_1_0_0 CancerParticipant object
        self.assertTrue(isinstance(migrated_participant, CancerParticipant_new))
        self._validate(migrated_participant)

        self.assertEqual(
            migrated_participant.tumourSamples[0].tumourType,
            old_participant.cancerSamples[0].tumorType.upper()
        )

        self.assertEqual(
            migrated_participant.tumourSamples[0].tumourSubType,
            old_participant.cancerSamples[0].tumorSubType
        )

        self.assertEqual(
            migrated_participant.tumourSamples[0].tumourContent,
            old_participant.cancerSamples[0].tumorContent
        )

        self.assertEqual(
            migrated_participant.additionalInformation,
            old_participant.cancerDemographics.additionalInformation
        )
        self.assertEqual(
            migrated_participant.assignedICD10,
            old_participant.cancerDemographics.assignedICD10
        )

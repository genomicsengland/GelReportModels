from unittest import TestCase

from protocols.reports_3_0_0 import CancerParticipant as CancerParticipant_old
from protocols.participant_1_0_0 import CancerParticipant as CancerParticipant_new
from protocols.migration.migration_reports_3_0_0_to_participant_1_0_0 import MigrateReports3ToParticipant1
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.util.dependency_manager import VERSION_400, VERSION_300


class TestMigrateReports3ToParticipant1(TestCase):

    def test_migrate_cancer_participant(self):

        old_participant = GenericFactoryAvro.get_factory_avro(CancerParticipant_old, VERSION_300)()
        new_participant = GenericFactoryAvro.get_factory_avro(CancerParticipant_new, VERSION_400)()

        for cancer_sample in old_participant.cancerSamples:
            cancer_sample.tumorType = 'lung'
            cancer_sample.tumorSubType = 'mock_subtype'
            cancer_sample.tumorContent = 'High'
            cancer_sample.labId = "1"

        # Check old_participant is a valid reports_3_0_0 CancerParticipant object
        self.assertTrue(isinstance(old_participant, CancerParticipant_old))
        self.assertTrue(old_participant.validate(jsonDict=old_participant.toJsonDict()))

        # Check new_participant is a valid participant_1_0_0 CancerParticipant object
        self.assertTrue(isinstance(new_participant, CancerParticipant_new))
        self.assertTrue(new_participant.validate(jsonDict=new_participant.toJsonDict()))

        # Perform the migration of old_participant from reports_3_0_0 to participant_1_0_0
        migrated_participant = MigrateReports3ToParticipant1().migrate_cancer_participant(old_participant)

        # Check migrated_participant is a valid participant_1_0_0 CancerParticipant object
        self.assertTrue(isinstance(migrated_participant, CancerParticipant_new))
        self.assertTrue(migrated_participant.validate(jsonDict=migrated_participant.toJsonDict()))

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

from copy import deepcopy
from unittest import TestCase

from protocols.tests import get_valid_cancer_participant_3_0_0
from protocols.tests import get_valid_empty_cancer_participant_1_0_0
from protocols.reports_3_0_0 import CancerParticipant as CancerParticipant_old
from protocols.participant_1_0_0 import CancerParticipant as CancerParticipant_new
from protocols.migration.migration_reports_3_0_0_to_participant_1_0_0 import MigrateReports3ToParticipant1


class TestMigrateReports3ToParticipant1(TestCase):

    def test_migrate_cancer_participant(self):

        old_participant = get_valid_cancer_participant_3_0_0()
        new_participant = get_valid_empty_cancer_participant_1_0_0()

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
            migrated_participant.additionalInformation,
            old_participant.cancerDemographics.additionalInformation
        )
        self.assertEqual(
            migrated_participant.assignedICD10,
            old_participant.cancerDemographics.assignedICD10
        )

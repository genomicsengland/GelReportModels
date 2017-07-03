from copy import deepcopy
from unittest import TestCase

from protocols.migration.migration_reports_3_1_0_to_participant_1_0_0 import MigrateReports3ToParticipant1
from protocols.participant_1_0_0 import CancerParticipant as CancerParticipant_new
from protocols.reports_3_1_0 import CancerParticipant as CancerParticipant_old
from protocols.tests import MockTestObject


class TestMigrateReports3ToParticipant1(TestCase):

    def test_migrate_cancer_participant(self):

        old_participant = MockTestObject(object_type=CancerParticipant_old).get_valid_empty_object()
        old_participant.cancerDemographics.sex = 'M'
        old_participant.cancerSamples[0].sampleType = 'tumor'
        old_participant.cancerSamples[0].labId = '1'
        additional_sample = deepcopy(old_participant.cancerSamples[0])
        old_participant.cancerSamples.append(additional_sample)
        old_participant.cancerSamples[1].sampleType = 'germline'
        old_participant.cancerSamples[1].labId = '2'

        new_participant = MockTestObject(object_type=CancerParticipant_new).get_valid_empty_object()
        new_participant.sex = 'M'
        new_participant.germlineSamples.labSampleId = 1
        new_participant.tumourSamples.tumourId = 1
        new_participant.tumourSamples.labSampleId = 1
        new_participant.readyForAnalysis = True
        new_participant.sex = 'UNKNOWN'

        matchedSample = new_participant.matchedSamples
        new_participant.matchedSamples = [matchedSample]

        germlineSample = new_participant.germlineSamples
        new_participant.germlineSamples = [germlineSample]

        tumourSample = new_participant.tumourSamples
        new_participant.tumourSamples = [tumourSample]

        # Check old_participant is a valid reports_3_1_0 CancerParticipant object
        self.assertTrue(old_participant.validate(jsonDict=old_participant.toJsonDict()))

        # Check new_participant is a valid participant_1_0_0 CancerParticipant object
        self.assertTrue(new_participant.validate(jsonDict=new_participant.toJsonDict()))

        # Perform the migration of old_participant from reports_3_1_0 to participant_1_0_0
        migrated_participant = MigrateReports3ToParticipant1().migrate_cancer_participant(old_participant)

        # Check migrated_participant is a valid participant_1_0_0 CancerParticipant object
        self.assertTrue(migrated_participant.validate(jsonDict=migrated_participant.toJsonDict()))

        self.assertEqual(
            migrated_participant.additionalInformation,
            old_participant.cancerDemographics.additionalInformation
        )
        self.assertEqual(
            migrated_participant.assignedICD10,
            old_participant.cancerDemographics.assignedIcd10
        )

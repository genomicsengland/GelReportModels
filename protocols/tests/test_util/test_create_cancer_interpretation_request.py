from unittest import TestCase

from protocols import reports_4_0_0
from protocols import participant_1_0_0
from protocols.util.dependency_manager import VERSION_400
from protocols.reports_4_0_0 import CancerInterpretationRequest
from protocols.util import create_cancer_interpretation_request
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.util.factories.participant_1_0_0_factories import CancerParticipantFactory


class TestCreateCancerInterpretationRequest(TestCase):

    def test_create_cancer_interpretation_request(self):
        test_analysis_uri = ''
        GenericFactoryAvro.register_factory(clazz=participant_1_0_0.CancerParticipant, factory=CancerParticipantFactory)
        test_cancer_participant = GenericFactoryAvro.get_factory_avro(clazz=participant_1_0_0.CancerParticipant, version=VERSION_400)()
        matched_samples = participant_1_0_0.MatchedSamples(
            germlineSampleId='test_germline_id', tumourSampleId='test_tumour_id'
        )
        test_cancer_participant.matchedSamples = [matched_samples]
        test_annotation_file = GenericFactoryAvro.get_factory_avro(clazz=reports_4_0_0.File, version=VERSION_400)()
        test_bam = GenericFactoryAvro.get_factory_avro(clazz=reports_4_0_0.File, version=VERSION_400)()
        test_big_wig = GenericFactoryAvro.get_factory_avro(clazz=reports_4_0_0.File, version=VERSION_400)()
        test_vcf = GenericFactoryAvro.get_factory_avro(clazz=reports_4_0_0.File, version=VERSION_400)()
        test_version_control = GenericFactoryAvro.get_factory_avro(clazz=reports_4_0_0.ReportVersionControl, version=VERSION_400)()
        test_reported_somatic_variant = GenericFactoryAvro.get_factory_avro(clazz=reports_4_0_0.ReportedSomaticVariants, version=VERSION_400)()
        test_reported_somatic_structural_variant = GenericFactoryAvro.get_factory_avro(clazz=reports_4_0_0.ReportedSomaticStructuralVariants, version=VERSION_400)()

        test_request = create_cancer_interpretation_request(
            analysisUri=test_analysis_uri,
            annotationFile=test_annotation_file,
            bams=[test_bam],
            bigWigs=[test_big_wig],
            cancerParticipant=test_cancer_participant,
            internalStudyId='123456',
            reportRequestId='123456',
            reportVersion=1,
            structuralTieredVariants=[test_reported_somatic_structural_variant],
            tieredVariants=[test_reported_somatic_variant],
            tieringVersion='1',
            vcfs=[test_vcf],
            versionControl=test_version_control,
            workspace=['some_workspace'],
        )

        # Ensure create_cancer_interpretation_request returns a valid CancerInterpretationRequest object
        self.assertTrue(isinstance(test_request, CancerInterpretationRequest))
        self.assertTrue(test_request.validate(test_request.toJsonDict()))

from unittest import TestCase

from protocols.reports_4_0_0 import CancerInterpretationRequest
from protocols.reports_4_0_0 import FileType
from protocols.tests import get_valid_empty_cancer_participant_1_0_0
from protocols.tests import get_valid_empty_file_4_0_0
from protocols.tests import get_valid_empty_reported_somatic_variant_4_0_0
from protocols.tests import get_valid_report_version_control_4_0_0
from protocols.tests import get_valid_reported_somatic_structural_variant_4_0_0
from protocols.util import create_cancer_interpretation_request


class TestCreateCancerInterpretationRequest(TestCase):

    def test_create_cancer_interpretation_request(self):
        test_analysis_uri = ''
        test_cancer_participant = get_valid_empty_cancer_participant_1_0_0()
        test_annotation_file = get_valid_empty_file_4_0_0(file_type=FileType.ANN)
        test_bam = get_valid_empty_file_4_0_0(file_type=FileType.BAM)
        test_big_wig = get_valid_empty_file_4_0_0(file_type=FileType.BigWig)
        test_vcf = get_valid_empty_file_4_0_0(file_type=FileType.VCF_somatic_small)
        test_version_control = get_valid_report_version_control_4_0_0()
        test_reported_somatic_variant = get_valid_empty_reported_somatic_variant_4_0_0()
        test_reported_somatic_structural_variant = get_valid_reported_somatic_structural_variant_4_0_0()

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

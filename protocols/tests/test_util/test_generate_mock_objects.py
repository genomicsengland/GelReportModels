from unittest import TestCase

from protocols import reports_2_1_0
from protocols import reports_3_0_0
from protocols import reports_3_1_0
from protocols import reports_4_0_0
from protocols.util import generate_mock_objects


class TestGenerateMockObjects4(TestCase):

    model = reports_4_0_0

    def test_interpreted_genome_rd(self):
        """
        Ensure generate_mock_objects.get_valid_interpreted_genome_rd_4_0_0 returns a valid
        reports_4_0_0.InterpretedGenomeRD object
        """
        test_ig_rd = generate_mock_objects.get_valid_interpreted_genome_rd_4_0_0()
        self.assertTrue(isinstance(test_ig_rd, self.model.InterpretedGenomeRD))
        self.assertTrue(test_ig_rd.validate(test_ig_rd.toJsonDict()))

    def test_interpretation_request_rd(self):
        """
        Ensure generate_mock_objects.get_valid_interpretation_request_rd_4_0_0 returns a valid
        reports_4_0_0.InterpretationRequestRD object
        """
        test_ir_rd = generate_mock_objects.get_valid_interpretation_request_rd_4_0_0()
        self.assertTrue(isinstance(test_ir_rd, self.model.InterpretationRequestRD))
        self.assertTrue(test_ir_rd.validate(test_ir_rd.toJsonDict()))

    def test_cancer_interpreted_genome(self):
        """
        Ensure generate_mock_objects.get_valid_cancer_interpreted_genome_4_0_0 returns a valid
        reports_4_0_0.CancerInterpretedGenome object
        """
        test_ir_rd = generate_mock_objects.get_valid_cancer_interpreted_genome_4_0_0()
        self.assertTrue(isinstance(test_ir_rd, self.model.CancerInterpretedGenome))
        self.assertTrue(test_ir_rd.validate(test_ir_rd.toJsonDict()))

    def test_cancer_interpretation_request(self):
        """
        Ensure generate_mock_objects.get_valid_cancer_interpretation_request_4_0_0 returns a valid
        reports_4_0_0.CancerInterpretationRequest object
        """
        test_cir = generate_mock_objects.get_valid_cancer_interpretation_request_4_0_0()
        self.assertTrue(isinstance(test_cir, self.model.CancerInterpretationRequest))
        self.assertTrue(test_cir.validate(test_cir.toJsonDict()))

    def test_clinical_report_cancer(self):
        """
        Ensure generate_mock_objects.get_valid_clinical_report_cancer_4_0_0 returns a valid
        reports_4_0_0.ClinicalReportCancer object
        """
        test_cir = generate_mock_objects.get_valid_clinical_report_cancer_4_0_0()
        self.assertTrue(isinstance(test_cir, self.model.ClinicalReportCancer))
        self.assertTrue(test_cir.validate(test_cir.toJsonDict()))

    def test_rd_exit_questionnaire(self):
        """
        Ensure generate_mock_objects.get_valid_rd_exit_questionnaire_4_0_0 returns a valid
        reports_4_0_0.RareDiseaseExitQuestionnaire object
        """
        test_cir = generate_mock_objects.get_valid_rd_exit_questionnaire_4_0_0()
        self.assertTrue(isinstance(test_cir, self.model.RareDiseaseExitQuestionnaire))
        self.assertTrue(test_cir.validate(test_cir.toJsonDict()))

    def test_clinical_report_rd(self):
        """
        Ensure generate_mock_objects.get_valid_clinical_report_rd_4_0_0 returns a valid
        reports_4_0_0.ClinicalReportRD object
        """
        test_cr_rd = generate_mock_objects.get_valid_clinical_report_rd_4_0_0()
        self.assertTrue(isinstance(test_cr_rd, self.model.ClinicalReportRD))
        self.assertTrue(test_cr_rd.validate(test_cr_rd.toJsonDict()))


class TestGenerateMockObjects31(TestCase):

    model = reports_3_1_0

    def test_interpreted_genome_rd(self):
        """
        Ensure generate_mock_objects.get_valid_interpreted_genome_rd_3_1_0 returns a valid
        reports_3_1_0.InterpretedGenomeRD object
        """
        test_ig_rd = generate_mock_objects.get_valid_interpreted_genome_rd_3_1_0()
        self.assertTrue(isinstance(test_ig_rd, self.model.InterpretedGenomeRD))
        self.assertTrue(test_ig_rd.validate(test_ig_rd.toJsonDict()))

    def test_interpretation_request_rd(self):
        """
        Ensure generate_mock_objects.get_valid_interpretation_request_rd_3_1_0 returns a valid
        reports_3_1_0.InterpretationRequestRD object
        """
        test_ir_rd = generate_mock_objects.get_valid_interpretation_request_rd_3_1_0()
        self.assertTrue(isinstance(test_ir_rd, self.model.InterpretationRequestRD))
        self.assertTrue(test_ir_rd.validate(test_ir_rd.toJsonDict()))

    def test_cancer_interpreted_genome(self):
        """
        Ensure generate_mock_objects.get_valid_cancer_interpreted_genome_3_1_0 returns a valid
        reports_3_1_0.CancerInterpretedGenome object
        """
        test_ir_rd = generate_mock_objects.get_valid_cancer_interpreted_genome_3_1_0()
        self.assertTrue(isinstance(test_ir_rd, self.model.CancerInterpretedGenome))
        self.assertTrue(test_ir_rd.validate(test_ir_rd.toJsonDict()))

    def test_cancer_interpretation_request(self):
        """
        Ensure generate_mock_objects.get_valid_cancer_interpretation_request_3_1_0 returns a valid
        reports_3_1_0.CancerInterpretationRequest object
        """
        test_cir = generate_mock_objects.get_valid_cancer_interpretation_request_3_1_0()
        self.assertTrue(isinstance(test_cir, self.model.CancerInterpretationRequest))
        self.assertTrue(test_cir.validate(test_cir.toJsonDict()))

    def test_clinical_report_rd(self):
        """
        Ensure generate_mock_objects.get_valid_clinical_report_rd_3_1_0 returns a valid
        reports_3_1_0.ClinicalReportRD object
        """
        test_cr_rd = generate_mock_objects.get_valid_clinical_report_rd_3_1_0()
        self.assertTrue(isinstance(test_cr_rd, self.model.ClinicalReportRD))
        self.assertTrue(test_cr_rd.validate(test_cr_rd.toJsonDict()))

    def test_clinical_report_cancer(self):
        """
        Ensure generate_mock_objects.get_valid_clinical_report_cancer_3_1_0 returns a valid
        reports_3_1_0.ClinicalReportCancer object
        """
        test_cir = generate_mock_objects.get_valid_clinical_report_cancer_3_1_0()
        self.assertTrue(isinstance(test_cir, self.model.ClinicalReportCancer))
        self.assertTrue(test_cir.validate(test_cir.toJsonDict()))

    def test_rd_exit_questionnaire(self):
        """
        Ensure generate_mock_objects.get_valid_rd_exit_questionnaire_3_1_0 returns a valid
        reports_3_1_0.RareDiseaseExitQuestionnaire object
        """
        test_cir = generate_mock_objects.get_valid_rd_exit_questionnaire_3_1_0()
        self.assertTrue(isinstance(test_cir, self.model.RareDiseaseExitQuestionnaire))
        self.assertTrue(test_cir.validate(test_cir.toJsonDict()))

    def test_called_genotype(self):
        """
        Ensure generate_mock_objects.get_valid_called_genotype_3_1_0 returns a valid
        reports_3_1_0.CalledGenotype object
        """
        test_cg = generate_mock_objects.get_valid_called_genotype_3_1_0()
        self.assertTrue(isinstance(test_cg, self.model.CalledGenotype))
        self.assertTrue(test_cg.validate(test_cg.toJsonDict()))

    def test_report_event(self):
        """
        Ensure generate_mock_objects.get_valid_called_genotype_3_1_0 returns a valid
        reports_3_1_0.CalledGenotype object
        """
        test_re = generate_mock_objects.get_valid_report_event_3_1_0()
        self.assertTrue(isinstance(test_re, self.model.ReportEvent))
        self.assertTrue(test_re.validate(test_re.toJsonDict()))

    def test_cancer_participant(self):
        """
        Ensure generate_mock_objects.get_valid_cancer_participant_3_1_0 returns a valid
        reports_3_1_0.CancerParticipant object
        """
        test_participant = generate_mock_objects.get_valid_cancer_participant_3_1_0()
        self.assertTrue(isinstance(test_participant, self.model.CancerParticipant))
        self.assertTrue(test_participant.validate(test_participant.toJsonDict()))

    def test_reported_variant(self):
        """
        Ensure generate_mock_objects.get_valid_cancer_participant_3_1_0 returns a valid
        reports_3_1_0.CancerParticipant object
        """
        test_rv = generate_mock_objects.get_valid_reported_variant_3_1_0()
        self.assertTrue(isinstance(test_rv, self.model.ReportedVariant))
        self.assertTrue(test_rv.validate(test_rv.toJsonDict()))


class TestGenerateMockObjects3(TestCase):

    model = reports_3_0_0

    def test_interpreted_genome_rd(self):
        """
        Ensure generate_mock_objects.get_valid_interpreted_genome_rd_3_0_0 returns a valid
        reports_3_0_0.InterpretedGenomeRD object
        """
        test_ig_rd = generate_mock_objects.get_valid_interpreted_genome_rd_3_0_0()
        self.assertTrue(isinstance(test_ig_rd, self.model.InterpretedGenomeRD))
        self.assertTrue(test_ig_rd.validate(test_ig_rd.toJsonDict()))

    def test_interpretation_request_rd(self):
        """
        Ensure generate_mock_objects.get_valid_interpretation_request_rd_3_0_0 returns a valid
        reports_3_0_0.InterpretationRequestRD object
        """
        test_ir_rd = generate_mock_objects.get_valid_interpretation_request_rd_3_0_0()
        self.assertTrue(isinstance(test_ir_rd, self.model.InterpretationRequestRD))
        self.assertTrue(test_ir_rd.validate(test_ir_rd.toJsonDict()))

    def test_cancer_interpreted_genome(self):
        """
        Ensure generate_mock_objects.get_valid_cancer_interpreted_genome_3_0_0 returns a valid
        reports_3_0_0.CancerInterpretedGenome object
        """
        test_ir_rd = generate_mock_objects.get_valid_cancer_interpreted_genome_3_0_0()
        self.assertTrue(isinstance(test_ir_rd, self.model.CancerInterpretedGenome))
        self.assertTrue(test_ir_rd.validate(test_ir_rd.toJsonDict()))

    def test_cancer_interpretation_request(self):
        """
        Ensure generate_mock_objects.get_valid_cancer_interpretation_request_3_0_0 returns a valid
        reports_3_0_0.CancerInterpretationRequest object
        """
        test_cir = generate_mock_objects.get_valid_cancer_interpretation_request_3_0_0()
        self.assertTrue(isinstance(test_cir, self.model.CancerInterpretationRequest))
        self.assertTrue(test_cir.validate(test_cir.toJsonDict()))

    def test_clinical_report_rd(self):
        """
        Ensure generate_mock_objects.get_valid_clinical_report_rd_3_0_0 returns a valid
        reports_3_0_0.ClinicalReportRD object
        """
        test_cr_rd = generate_mock_objects.get_valid_clinical_report_rd_3_0_0()
        self.assertTrue(isinstance(test_cr_rd, self.model.ClinicalReportRD))
        self.assertTrue(test_cr_rd.validate(test_cr_rd.toJsonDict()))

    def test_clinical_report_cancer(self):
        """
        Ensure generate_mock_objects.get_valid_clinical_report_cancer_3_0_0 returns a valid
        reports_3_0_0.ClinicalReportCancer object
        """
        test_cir = generate_mock_objects.get_valid_clinical_report_cancer_3_0_0()
        self.assertTrue(isinstance(test_cir, self.model.ClinicalReportCancer))
        self.assertTrue(test_cir.validate(test_cir.toJsonDict()))

    def test_rd_exit_questionnaire(self):
        """
        Ensure generate_mock_objects.get_valid_rd_exit_questionnaire_3_0_0 returns a valid
        reports_3_0_0.RareDiseaseExitQuestionnaire object
        """
        test_cir = generate_mock_objects.get_valid_rd_exit_questionnaire_3_0_0()
        self.assertTrue(isinstance(test_cir, self.model.RareDiseaseExitQuestionnaire))
        self.assertTrue(test_cir.validate(test_cir.toJsonDict()))


class TestGenerateMockObjects21(TestCase):

    model = reports_2_1_0

    def test_interpreted_genome_rd(self):
        """
        Ensure generate_mock_objects.get_valid_interpreted_genome_rd_2_1_0 returns a valid
        reports_2_1_0.InterpretedGenomeRD object
        """
        test_ig_rd = generate_mock_objects.get_valid_interpreted_genome_rd_2_1_0()
        self.assertTrue(isinstance(test_ig_rd, self.model.InterpretedGenomeRD))
        self.assertTrue(test_ig_rd.validate(test_ig_rd.toJsonDict()))

    def test_interpretation_request_rd(self):
        """
        Ensure generate_mock_objects.get_valid_interpretation_request_rd_2_1_0 returns a valid
        reports_2_1_0.InterpretationRequestRD object
        """
        test_ir_rd = generate_mock_objects.get_valid_interpretation_request_rd_2_1_0()
        self.assertTrue(isinstance(test_ir_rd, self.model.InterpretationRequestRD))
        self.assertTrue(test_ir_rd.validate(test_ir_rd.toJsonDict()))

    def test_cancer_interpreted_genome(self):
        """
        Ensure generate_mock_objects.get_valid_cancer_interpreted_genome_2_1_0 returns a valid
        reports_2_1_0.CancerInterpretedGenome object
        """
        test_ir_rd = generate_mock_objects.get_valid_cancer_interpreted_genome_2_1_0()
        self.assertTrue(isinstance(test_ir_rd, self.model.CancerInterpretedGenome))
        self.assertTrue(test_ir_rd.validate(test_ir_rd.toJsonDict()))

    def test_cancer_interpretation_request(self):
        """
        Ensure generate_mock_objects.get_valid_cancer_interpretation_request_2_1_0 returns a valid
        reports_2_1_0.CancerInterpretationRequest object
        """
        test_cir = generate_mock_objects.get_valid_cancer_interpretation_request_2_1_0()
        self.assertTrue(isinstance(test_cir, self.model.CancerInterpretationRequest))
        self.assertTrue(test_cir.validate(test_cir.toJsonDict()))

    def test_clinical_report_rd(self):
        """
        Ensure generate_mock_objects.get_valid_clinical_report_rd_2_1_0 returns a valid
        reports_2_1_0.ClinicalReportRD object
        """
        test_cr_rd = generate_mock_objects.get_valid_clinical_report_rd_2_1_0()
        self.assertTrue(isinstance(test_cr_rd, self.model.ClinicalReportRD))
        self.assertTrue(test_cr_rd.validate(test_cr_rd.toJsonDict()))

    def test_clinical_report_cancer(self):
        """
        Ensure generate_mock_objects.get_valid_clinical_report_cancer_2_1_0 returns a valid
        reports_2_1_0.ClinicalReportCancer object
        """
        test_cir = generate_mock_objects.get_valid_clinical_report_cancer_2_1_0()
        self.assertTrue(isinstance(test_cir, self.model.ClinicalReportCancer))
        self.assertTrue(test_cir.validate(test_cir.toJsonDict()))

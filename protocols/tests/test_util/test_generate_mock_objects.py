from unittest import TestCase

from protocols import cva_0_3_1
from protocols import reports_2_1_0
from protocols import reports_3_0_0
from protocols import reports_3_1_0
from protocols import reports_4_0_0
from protocols import participant_1_0_3
from protocols import cva_0_4_0
from protocols import reports_4_2_0
from protocols import participant_1_0_4
from protocols import participant_1_0_3
from protocols import system_0_1_0
from protocols.util import generate_mock_objects


class TestGenerateMockObjects420(TestCase):

    model = reports_4_2_0

    def test_interpretation_request_rd(self):
        """
        Ensure generate_mock_objects.get_valid_interpretation_request_rd_4_2_0 returns a valid
        reports_4_2_0.InterpretationRequestRD object
        """
        test_ir_rd = generate_mock_objects.get_valid_interpretation_request_rd_4_2_0()
        self.assertTrue(isinstance(test_ir_rd, self.model.InterpretationRequestRD))
        self.assertTrue(test_ir_rd.validate(test_ir_rd.toJsonDict()))

    def test_cancer_interpretation_request(self):
        """
        Ensure generate_mock_objects.get_valid_cancer_interpretation_request_4_2_0 returns a valid
        reports_4_2_0.CancerInterpretationRequest object
        """
        test_ir_rd = generate_mock_objects.get_valid_cancer_interpretation_request_4_2_0()
        self.assertTrue(isinstance(test_ir_rd, self.model.CancerInterpretationRequest))
        self.assertTrue(test_ir_rd.validate(test_ir_rd.toJsonDict()))


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


class TestGenerateMockObjectsCVA031(TestCase):

    model = cva_0_3_1

    def test_tiered_variant_inject_rd(self):
        """
        Ensure generate_mock_objects.get_valid_tiered_variant_inject_rd_0_3_1 returns a valid
        cva_0_3_1.TieredVariantInjectRD object
        """
        test_tvi_rd = generate_mock_objects.get_valid_tiered_variant_inject_rd_0_3_1()
        self.assertTrue(isinstance(test_tvi_rd, self.model.TieredVariantInjectRD))
        self.assertTrue(test_tvi_rd.validate(test_tvi_rd.toJsonDict()))

    def test_reported_variant_inject_rd(self):
        """
        Ensure generate_mock_objects.get_valid_reported_variant_inject_rd_0_3_1 returns a valid
        cva_0_3_1.ReportedVariantInjectRD object
        """
        test_tvi_rd = generate_mock_objects.get_valid_reported_variant_inject_rd_0_3_1()
        self.assertTrue(isinstance(test_tvi_rd, self.model.ReportedVariantInjectRD))
        self.assertTrue(test_tvi_rd.validate(test_tvi_rd.toJsonDict()))

    def test_candidate_variant_inject_rd(self):
        """
        Ensure generate_mock_objects.get_valid_candidate_variant_inject_rd_0_3_1 returns a valid
        cva_0_3_1.CandidateVariantInjectRD object
        """
        test_tvi_rd = generate_mock_objects.get_valid_candidate_variant_inject_rd_0_3_1()
        self.assertTrue(isinstance(test_tvi_rd, self.model.CandidateVariantInjectRD))
        self.assertTrue(test_tvi_rd.validate(test_tvi_rd.toJsonDict()))


class TestGenerateMockObjectsCVA040(TestCase):

    model = cva_0_4_0

    def test_tiered_variant_inject_rd(self):
        """
        Ensure generate_mock_objects.get_valid_tiered_variant_inject_rd_0_4_0 returns a valid
        cva_0_4_0.TieredVariantInjectRD object
        """
        test_tvi_rd = generate_mock_objects.get_valid_tiered_variant_inject_rd_0_4_0()
        self.assertTrue(isinstance(test_tvi_rd, self.model.TieredVariantInjectRD))
        self.assertTrue(test_tvi_rd.validate(test_tvi_rd.toJsonDict()))

    def test_tiered_variant_inject_cancer(self):
        """
        Ensure generate_mock_objects.get_valid_tiered_variant_inject_cancer_0_4_0 returns a valid
        cva_0_4_0.TieredVariantInjectCancer object
        """
        test_tvi_rd = generate_mock_objects.get_valid_tiered_variant_inject_cancer_0_4_0()
        self.assertTrue(isinstance(test_tvi_rd, self.model.TieredVariantInjectCancer))
        self.assertTrue(test_tvi_rd.validate(test_tvi_rd.toJsonDict()))

    def test_reported_variant_inject_rd(self):
        """
        Ensure generate_mock_objects.get_valid_reported_variant_inject_rd_0_4_0 returns a valid
        cva_0_4_0.ReportedVariantInjectRD object
        """
        test_tvi_rd = generate_mock_objects.get_valid_reported_variant_inject_rd_0_4_0()
        self.assertTrue(isinstance(test_tvi_rd, self.model.ReportedVariantInjectRD))
        self.assertTrue(test_tvi_rd.validate(test_tvi_rd.toJsonDict()))

    def test_reported_variant_inject_cancer(self):
        """
        Ensure generate_mock_objects.get_valid_reported_variant_inject_cancer_0_4_0 returns a valid
        cva_0_4_0.ReportedVariantInjectCancer object
        """
        test_tvi_rd = generate_mock_objects.get_valid_reported_variant_inject_cancer_0_4_0()
        self.assertTrue(isinstance(test_tvi_rd, self.model.ReportedVariantInjectCancer))
        self.assertTrue(test_tvi_rd.validate(test_tvi_rd.toJsonDict()))

    def test_candidate_variant_inject_rd(self):
        """
        Ensure generate_mock_objects.get_valid_candidate_variant_inject_rd_0_4_0 returns a valid
        cva_0_4_0.CandidateVariantInjectRD object
        """
        test_tvi_rd = generate_mock_objects.get_valid_candidate_variant_inject_rd_0_4_0()
        self.assertTrue(isinstance(test_tvi_rd, self.model.CandidateVariantInjectRD))
        self.assertTrue(test_tvi_rd.validate(test_tvi_rd.toJsonDict()))

    def test_candidate_variant_inject_cancer(self):
        """
        Ensure generate_mock_objects.get_valid_candidate_variant_inject_cancer_0_4_0 returns a valid
        cva_0_4_0.CandidateVariantInjectCancer object
        """
        test_tvi_rd = generate_mock_objects.get_valid_candidate_variant_inject_cancer_0_4_0()
        self.assertTrue(isinstance(test_tvi_rd, self.model.CandidateVariantInjectCancer))
        self.assertTrue(test_tvi_rd.validate(test_tvi_rd.toJsonDict()))

class TestGenerateMockObjectsSystem010(TestCase):

    model = system_0_1_0

    def test_datastore(self):
        """
        Ensure generate_mock_objects.get_valid_data_store_0_1_0 returns a valid
        system_0_1_0.DataStore object
        """
        test_datastore = generate_mock_objects.get_valid_data_store_0_1_0()
        self.assertTrue(isinstance(test_datastore, self.model.DataStore))
        self.assertTrue(test_datastore.validate(test_datastore.toJsonDict()))

    def test_api(self):
        """
        Ensure generate_mock_objects.get_valid_api_0_1_0 returns a valid
        system_0_1_0.API object
        """
        test_api = generate_mock_objects.get_valid_api_0_1_0()
        self.assertTrue(isinstance(test_api, self.model.API))
        self.assertTrue(test_api.validate(test_api.toJsonDict()))

    def test_dependencies(self):
        """
        Ensure generate_mock_objects.get_valid_dependencies_0_1_0 returns a valid
        system_0_1_0.Dependencies object
        """
        test_dependencies = generate_mock_objects.get_valid_dependencies_0_1_0()
        self.assertTrue(isinstance(test_dependencies, self.model.Dependencies))
        self.assertTrue(test_dependencies.validate(test_dependencies.toJsonDict()))

    def test_servicehealth(self):
        """
        Ensure generate_mock_objects.get_valid_servicehealth_0_1_0 returns a valid
        system_0_1_0.ServiceHealth object
        """
        test_servicehealth = generate_mock_objects.get_valid_servicehealth_0_1_0()
        self.assertTrue(isinstance(test_servicehealth, self.model.ServiceHealth))
        self.assertTrue(test_servicehealth.validate(test_servicehealth.toJsonDict()))


class TestGenerateMockObjectsParticipant103(TestCase):

    model = participant_1_0_3

    def test_tiered_variant_inject_rd(self):
        """
        Ensure generate_mock_objects.get_valid_cancer_participant_1_0_3 returns a valid
        participant_1_0_3.CancerParticipant object
        """
        test_participant = generate_mock_objects.get_valid_cancer_participant_1_0_3()
        self.assertTrue(isinstance(test_participant, self.model.CancerParticipant))
        self.assertTrue(test_participant.validate(test_participant.toJsonDict()))

    def test_cancer_participant(self):
        """
        Ensure generate_mock_objects.get_valid_cancer_participant_1_0_3 returns a valid
        participant_1_0_3.CancerParticipant object
        """
        test_tvi_rd = generate_mock_objects.get_valid_cancer_participant_1_0_3()
        self.assertTrue(isinstance(test_tvi_rd, self.model.CancerParticipant))
        self.assertTrue(test_tvi_rd.validate(test_tvi_rd.toJsonDict()))


class TestGenerateMockObjectsParticipant104(TestCase):

    model = participant_1_0_4

    def test_cancer_participant(self):
        """
        Ensure generate_mock_objects.get_valid_cancer_participant_1_0_4 returns a valid
        participant_1_0_4.CancerParticipant object
        """
        test_tvi_rd = generate_mock_objects.get_valid_cancer_participant_1_0_4()
        self.assertTrue(isinstance(test_tvi_rd, self.model.CancerParticipant))
        self.assertTrue(test_tvi_rd.validate(test_tvi_rd.toJsonDict()))

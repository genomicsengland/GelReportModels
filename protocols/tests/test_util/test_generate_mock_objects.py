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


class TestGenerateMockObjects31(TestCase):

    model = reports_3_1_0

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


class TestGenerateMockObjects21(TestCase):

    model = reports_2_1_0

    def test_interpreted_genome_rd(self):
        """
        Ensure generate_mock_objects.get_valid_interpreted_genome_rd_3_0_0 returns a valid
        reports_3_0_0.InterpretedGenomeRD object
        """
        test_ig_rd = generate_mock_objects.get_valid_interpreted_genome_rd_2_1_0()
        self.assertTrue(isinstance(test_ig_rd, self.model.InterpretedGenomeRD))
        self.assertTrue(test_ig_rd.validate(test_ig_rd.toJsonDict()))

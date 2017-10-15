from unittest import TestCase

import factory

from protocols.ga4gh_3_0_0 import Variant
from protocols.reports_4_1_0 import CancerExitQuestionnaire
from protocols.util.factories.ga4gh_factories import GA4GHVariantFactory, CallFactory
from protocols.util.factories.reports_4_1_0_factories import CancerExitQuestionnaireFactory
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.cva_0_4_0 import TieredVariantInjectRD, TieredVariantInjectCancer
import protocols.reports_4_2_0
import protocols.reports_4_1_0
import protocols.reports_3_0_0
from protocols.util.dependency_manager import VERSION_430, VERSION_410, VERSION_300


class TestGA4GHVariantFactory(TestCase):

    variant_factory = GA4GHVariantFactory
    call_factory = CallFactory

    def test_create_random_variant(self):
        """

        Variant is created and is a valid one
        """
        variant = self.variant_factory()
        self.assertTrue(variant.validate(variant.toJsonDict()))

    def test_overwrite_properties(self):
        """

        Variant is created with some defined properties, simple and complex
        :return:
        """
        variant = self.variant_factory(referenceBases='T', referenceName='X', start=12)
        self.assertEqual(variant.referenceBases, 'T')
        self.assertEqual(variant.referenceName, 'X')
        self.assertEqual(variant.start, 12)
        self.assertTrue(variant.validate(variant.toJsonDict()))

        calls = self.call_factory.create_batch(4, genotypeLikelihood=[1])
        variant = self.variant_factory(calls=calls)
        self.assertTrue(variant.validate(variant.toJsonDict()))
        for call in variant.calls:
            self.assertEqual(call.genotypeLikelihood[0], 1)

    def test_extending_factories(self):
        """

        Factories can be extended to solve complex situation, in this test cases we are going to create a factory
        that is able to produce a list variants in a region (X: 1000-1020) each 2 bases - Note this is a very silly
        example which won't work in real life because relay on the counter to set the beginning of the sequence.
        """

        class JumpingGA4GHVariantFactory(GA4GHVariantFactory):
            class Meta:
                model = Variant

            referenceName = 'X'
            @factory.sequence
            def start(n):
                pos = n*2 + 1000
                if pos >= 1020:
                    return 1020
                else:
                    return pos
            end = start

        # Reset the content, because the library is does not
        GA4GHVariantFactory._meta._counter = None
        for i, v in enumerate(JumpingGA4GHVariantFactory.create_batch(5)):
            self.assertEqual(v.start, i*2 + 1000)

    def test_cancer_exitquestionnaire_factory(self):
        batch = CancerExitQuestionnaireFactory.create_batch(1000)
        validation_results = map(lambda x: CancerExitQuestionnaire.validate(x.toJsonDict()), batch)
        self.assertNotIn(False, validation_results)


class TestGenericFactory(TestCase):

    def test_tiered_variant_inject_rd_factory(self):
        tiered_variant_inject_factory = GenericFactoryAvro.get_factory_avro(TieredVariantInjectRD)
        instance = tiered_variant_inject_factory()
        self.assertTrue(instance.validate(instance.toJsonDict()))

    def test_tiered_variant_inject_cancer_factory(self):
        tiered_variant_inject_factory = GenericFactoryAvro.get_factory_avro(TieredVariantInjectCancer)
        instance = tiered_variant_inject_factory()
        self.assertTrue(instance.validate(instance.toJsonDict()))

    def test_interpretation_request(self):
        # get an interpretation request RD for reports 4.2.0
        interpretation_request_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_4_2_0.InterpretationRequestRD,
            version = VERSION_430
        )
        instance = interpretation_request_factory()
        self.assertTrue(instance.validate(instance.toJsonDict()))
        # get an interpretation request RD for reports 4.1.0
        interpretation_request_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_4_1_0.InterpretationRequestRD,
            version=VERSION_410
        )
        instance = interpretation_request_factory()
        self.assertTrue(instance.validate(instance.toJsonDict()))
        # get an interpretation request RD for reports 3.1.0
        interpretation_request_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_3_0_0.InterpretationRequestRD,
            version=VERSION_300
        )
        instance = interpretation_request_factory()
        self.assertTrue(instance.validate(instance.toJsonDict()))

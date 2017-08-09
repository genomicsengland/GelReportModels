from unittest import TestCase

import factory

from models.ga4ghvariant import GA4GHVariant
from protocols.util.factories import GA4GHVariantFactory, CallFactory


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
                model = GA4GHVariant

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




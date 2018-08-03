import itertools

import factory.fuzzy

from protocols.ga4gh_3_0_0 import Variant, Call
from protocols.util.dependency_manager import VERSION_500
from protocols.util.factories.avro_factory import FactoryAvro, GenericFactoryAvro


class GA4GHVariantFactory(FactoryAvro):
    def __init__(self, *args, **kwargs):
        super(GA4GHVariantFactory, self).__init__(*args, **kwargs)

    class Meta:
        model = Variant

    _version = VERSION_500

    start = factory.fuzzy.FuzzyInteger(1, 10000000)
    referenceBases = factory.fuzzy.FuzzyChoice(['A', 'T', 'C', 'G'])
    alternateBases = factory.LazyAttribute(lambda x: [factory.fuzzy.FuzzyChoice(['A', 'T', 'C', 'G']).fuzz()])
    qual = factory.fuzzy.FuzzyInteger(1, 600)
    referenceName = factory.fuzzy.FuzzyChoice(list(map(str, range(1, 23))) + ['X', 'Y', 'MT'])

    @factory.post_generation
    def calls(self, create, extacted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if not extacted:
            CallFactory._meta._counter = None
            extacted = CallFactory.create_batch(4)

        # A list of groups were passed in, use them
        for call in extacted:
            if call:
                self.calls.append(call)


class CallFactory(FactoryAvro):
    def __init__(self, *args, **kwargs):
        super(CallFactory, self).__init__(*args, **kwargs)

    class Meta:
        model = Call

    _version = VERSION_500

    callSetName = factory.Sequence(lambda n: 'Sample%d' % n)
    callSetId = factory.Sequence(lambda n: '%d' % n)
    genotype = factory.fuzzy.FuzzyChoice(
        [list(g) for g in itertools.permutations([1, 0], 2)]
    )
    genotypeLikelihood = factory.LazyAttribute(lambda gl: [factory.fuzzy.FuzzyFloat(0, 1).fuzz() for _ in range(0, 2)])
    info = factory.LazyAttribute(lambda dp: {'DP': [str(factory.fuzzy.FuzzyInteger(0, 100).fuzz()) for _ in range(0, 2)]})

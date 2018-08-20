from random import randint
import factory.fuzzy
from protocols.util.dependency_manager import VERSION_500
from protocols.reports_4_2_0 import (
    CancerExitQuestionnaire,
    CancerSomaticVariantLevelQuestions,
    CancerGermlineVariantLevelQuestions,
    CancerCaseLevelQuestions
)
from protocols.util.factories.avro_factory import FactoryAvro


def aux_ramdom_variant_method():
    chr = factory.fuzzy.FuzzyChoice(list(map(str, range(1, 23))) + ['X', 'Y', 'MT']).fuzz()
    position = factory.fuzzy.FuzzyInteger(1, 10000000).fuzz()
    reference = factory.fuzzy.FuzzyChoice(['A', 'T', 'C', 'G']).fuzz()
    alternate = factory.fuzzy.FuzzyChoice(['A', 'T', 'C', 'G']).fuzz()
    while alternate == reference:
        alternate = factory.fuzzy.FuzzyChoice(['A', 'T', 'C', 'G']).fuzz()

    return '{chr}: {pos} {ref} > {alt}'.format(chr=chr, pos=position, ref=reference, alt=alternate)


class CancerCaseLevelQuestionsFactory(FactoryAvro):
    class Meta:
        model = CancerCaseLevelQuestions

    _version = VERSION_500

    total_review_time = factory.fuzzy.FuzzyFloat(1.0, 10.0)
    mdt1_time = factory.fuzzy.FuzzyFloat(1.0, 10.0,)
    mdt2_time = factory.fuzzy.FuzzyChoice([None, factory.fuzzy.FuzzyFloat(1.0, 10.0).fuzz()])
    validation_assay_time = factory.fuzzy.FuzzyChoice([None, factory.fuzzy.FuzzyFloat(1.0, 10.0).fuzz()])
    wet_validation_time = factory.fuzzy.FuzzyChoice([None, factory.fuzzy.FuzzyFloat(1.0, 10.0).fuzz()])
    analytical_validation_time = factory.fuzzy.FuzzyChoice([None, factory.fuzzy.FuzzyFloat(1.0, 10.0).fuzz()])
    primary_reporting_time = factory.fuzzy.FuzzyFloat(1.0, 10.0)
    primary_authorisation_time = factory.fuzzy.FuzzyFloat(1.0, 10.0)
    report_distribution_time = factory.fuzzy.FuzzyFloat(1.0, 10.0)
    total_time = factory.fuzzy.FuzzyFloat(1.0, 10.0)



class CancerSomaticVariantLevelQuestionsFactory(FactoryAvro):
    class Meta:
        model = CancerSomaticVariantLevelQuestions

    _version = VERSION_500

    variantDetails = factory.LazyAttribute(lambda x: aux_ramdom_variant_method())


class CancerGermlineVariantLevelQuestionsFactory(FactoryAvro):
    class Meta:
        model = CancerGermlineVariantLevelQuestions

    _version = VERSION_500

    variantDetails = factory.LazyAttribute(lambda x: aux_ramdom_variant_method())


class CancerExitQuestionnaireFactory(FactoryAvro):
    class Meta:
        model = CancerExitQuestionnaire

    _version = VERSION_500

    caseLevelQuestions = factory.SubFactory(CancerCaseLevelQuestionsFactory)
    somaticVariantLevelQuestions = factory.LazyAttribute(lambda x: [i for i in CancerSomaticVariantLevelQuestionsFactory.create_batch(randint(0, 10))])
    germlineVariantLevelQuestions = factory.LazyAttribute(lambda x: [i for i in CancerGermlineVariantLevelQuestionsFactory.create_batch(randint(0, 10))])

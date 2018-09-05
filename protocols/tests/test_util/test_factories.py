from unittest import TestCase

import factory

import protocols.reports_4_0_0
import protocols.reports_5_0_0
import protocols.reports_4_2_0
import protocols.reports_3_0_0
from protocols.ga4gh_3_0_0 import Variant
from protocols.util.dependency_manager import VERSION_300, VERSION_400, VERSION_500, VERSION_61
import protocols.cva_1_0_0 as cva_1_0_0
from protocols.util.factories.avro_factory import FactoryAvro
from protocols.util.factories.ga4gh_factories import CallFactory
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.util.factories.ga4gh_factories import GA4GHVariantFactory
from protocols.util.factories.reports_3_0_0_factories import CancerReportedVariantsFactory
from protocols.util.factories.reports_4_3_0_factories import CancerExitQuestionnaireFactory


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
        validation_results = map(lambda x: x.validate(x.toJsonDict()), batch)
        self.assertNotIn(False, validation_results)


class TestGenericFactory(TestCase):

    def test_tiered_variant_inject_rd_factory(self):
        tiered_variant_inject_factory = GenericFactoryAvro.get_factory_avro(
            cva_1_0_0.TieredVariantInjectRD,
            version=VERSION_61
        )
        instance = tiered_variant_inject_factory()
        self.assertTrue(instance.validate(instance.toJsonDict()))

    def test_tiered_variant_inject_cancer_factory(self):
        tiered_variant_inject_factory = GenericFactoryAvro.get_factory_avro(
            cva_1_0_0.TieredVariantInjectCancer,
            version=VERSION_61
        )
        instance = tiered_variant_inject_factory()
        self.assertTrue(instance.validate(instance.toJsonDict()))

    def test_interpretation_request(self):
        # get an interpretation request RD for reports 4.2.0
        interpretation_request_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_4_2_0.InterpretationRequestRD,
            version = VERSION_500
        )
        instance = interpretation_request_factory()
        self.assertTrue(instance.validate(instance.toJsonDict()))
        # get an interpretation request RD for reports 4.0.0
        interpretation_request_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_4_0_0.InterpretationRequestRD,
            version=VERSION_400
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

    def test_batch(self):
        # builds a batch of 5 interpretation requests
        interpretation_request_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_4_2_0.InterpretationRequestRD,
            version=VERSION_500
        )
        instances = interpretation_request_factory.create_batch(5)
        for instance in instances:
            self.assertTrue(instance.validate(instance.toJsonDict()))
        self.assertTrue(instances[0].interpretationRequestId != instances[1].interpretationRequestId)


        GenericFactoryAvro.register_factory(protocols.ga4gh_3_0_0.Variant, GA4GHVariantFactory)
        GenericFactoryAvro.get_factory_avro(protocols.ga4gh_3_0_0.Variant)

    def test_register_custom_factory(self):
        ## registering GA4GH variant factory
        GenericFactoryAvro.register_factory(Variant, GA4GHVariantFactory, version="4.0.0")
        factory = GenericFactoryAvro.get_factory_avro(Variant, "4.0.0")
        instances = factory.create_batch(5)
        for instance in instances:
            self.assertTrue(instance.validate(instance.toJsonDict()))
        self.assertTrue(instance.referenceBases in ["A", "C", "G", "T"])

        ## register CancerReportedVariantsFactory
        GenericFactoryAvro.register_factory(
            protocols.reports_3_0_0.ReportedVariantCancer, CancerReportedVariantsFactory, version="3.0.0"
        )
        factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_3_0_0.CancerInterpretationRequest, "3.0.0"
        )
        instances = factory.create_batch(5)
        for instance in instances:
            self.assertTrue(instance.validate(instance.toJsonDict()))
            for tiered_variant in instance.TieredVariants:
                self.assertTrue(tiered_variant.reportedVariantCancer.reference in ["A", "C", "G", "T"])
                self.assertTrue(tiered_variant.reportedVariantCancer.alternate in ["A", "C", "G", "T"])

    def test_nullable_fields(self):
        # creates a factory for File not filling nullable fields and registers it in cache
        # as a factory that fill nullable fields
        # NOTE: this is the workaround to circumvent the loop in model definition
        file_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_4_2_0.File,
            VERSION_500,
            False,
            False
        )
        GenericFactoryAvro.register_factory(
            protocols.reports_4_2_0.File,
            file_factory,
            VERSION_500,
            True
        )
        # get an interpretation request RD for reports 4.2.0
        interpretation_request_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_4_2_0.InterpretationRequestRD,
            version = VERSION_500,
            fill_nullables=True
        )
        instance = interpretation_request_factory()
        self.assertTrue(instance.validate(instance.toJsonDict()))

    def test_custom_fields(self):

        # get an interpretation request RD for reports 4.2.0
        interpretation_request_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_4_2_0.InterpretationRequestRD,
            version = VERSION_500
        )
        instance = interpretation_request_factory(analysisReturnUri = "myURI")
        self.assertTrue(instance.validate(instance.toJsonDict()))
        self.assertTrue(instance.analysisReturnUri == "myURI")

    def test_custom_fields2(self):

        # get an interpretation request RD for reports 4.2.0
        version_control_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_4_2_0.ReportVersionControl,
            version = VERSION_500
        )
        instance_vc = version_control_factory(gitVersionControl = "4.3.0-SNAPSHOT")
        self.assertTrue(instance_vc.validate(instance_vc.toJsonDict()))
        interpretation_request_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_4_2_0.InterpretationRequestRD,
            version=VERSION_500
        )
        instance_ir = interpretation_request_factory(versionControl=instance_vc)
        self.assertTrue(instance_ir.validate(instance_ir.toJsonDict()))
        self.assertTrue(instance_ir.versionControl.gitVersionControl == "4.3.0-SNAPSHOT")

    def test_register_custom_factory(self):

        # creates a custom factory and registers it
        class ReportVersionControlFactory(FactoryAvro):
            def __init__(self, *args, **kwargs):
                super(ReportVersionControlFactory, self).__init__(*args, **kwargs)

            class Meta:
                model = protocols.reports_4_2_0.ReportVersionControl

            _version = VERSION_500
            gitVersionControl = "4.3.0-SNAPSHOT"

        GenericFactoryAvro.register_factory(
            protocols.reports_4_2_0.ReportVersionControl,
            ReportVersionControlFactory,
            version=VERSION_500
        )

        interpretation_request_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_4_2_0.InterpretationRequestRD,
            version=VERSION_500
        )
        instance_ir = interpretation_request_factory()
        self.assertTrue(instance_ir.validate(instance_ir.toJsonDict()))
        self.assertTrue(instance_ir.versionControl.gitVersionControl == "4.3.0-SNAPSHOT")

        # now creates another factory generating values for nullable fields
        file_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_4_2_0.File,
            VERSION_500,
            False,
            False
        )
        GenericFactoryAvro.register_factory(
            protocols.reports_4_2_0.File,
            file_factory,
            VERSION_500,
            True
        )
        interpretation_request_factory2 = GenericFactoryAvro.get_factory_avro(
            protocols.reports_4_2_0.InterpretationRequestRD,
            version=VERSION_500,
            fill_nullables=True
        )
        instance_ir2 = interpretation_request_factory2()
        self.assertTrue(instance_ir2.validate(instance_ir2.toJsonDict()))
        self.assertFalse(instance_ir2.versionControl.gitVersionControl == "4.3.0-SNAPSHOT")

        # now registers the factory for ReportVersionControl when filling nullables
        GenericFactoryAvro.register_factory(
            protocols.reports_4_2_0.ReportVersionControl,
            ReportVersionControlFactory,
            version=VERSION_500,
            fill_nullables=True
        )
        instance_ir3 = interpretation_request_factory2()
        self.assertTrue(instance_ir3.validate(instance_ir3.toJsonDict()))
        self.assertTrue(instance_ir3.versionControl.gitVersionControl == "4.3.0-SNAPSHOT")

    def test_custom_fields(self):

        # get an interpretation request RD for reports 4.2.0
        interpretation_request_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_4_2_0.InterpretationRequestRD,
            version=VERSION_500
        )
        instance = interpretation_request_factory(analysisReturnUri = "myURI")
        self.assertTrue(instance.validate(instance.toJsonDict()))
        self.assertTrue(instance.analysisReturnUri == "myURI")

    def test_build_version_with_hotfix(self):

        # get an interpretation request RD for reports 5.0.0
        interpretation_request_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_5_0_0.InterpretationRequestRD,
            version=VERSION_61
        )
        instance = interpretation_request_factory()
        self.assertTrue(instance.validate(instance.toJsonDict()))

        # now try the same with the build version including the hotfix version
        interpretation_request_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_5_0_0.InterpretationRequestRD,
            version="6.1.0"
        )
        instance = interpretation_request_factory()
        self.assertTrue(instance.validate(instance.toJsonDict()))

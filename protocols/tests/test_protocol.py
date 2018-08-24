from unittest import TestCase

from protocols import reports_3_0_0
from protocols.reports_6_0_0 import ReportEvent
from protocols.util.dependency_manager import VERSION_300
from protocols.util.factories.avro_factory import GenericFactoryAvro


class TestValidate(TestCase):

    def test_validate_debug(self):
        object_type = reports_3_0_0.ReportedSomaticStructuralVariants
        variant = GenericFactoryAvro.get_factory_avro(clazz=object_type, version=VERSION_300)()
        variant.reportedStructuralVariantCancer.end = None

        # Check variant is not a valid ReportedSomaticStructuralVariants object
        self.assertFalse(variant.validate(jsonDict=variant.toJsonDict()))

        # Check the result of validation_result is False
        validation_result = variant.validate(jsonDict=variant.toJsonDict(), verbose=True)
        self.assertFalse(validation_result.result)

        # Check the validation returns the expected messages
        expected_message_2 = 'Class: [ReportedStructuralVariantCancer] expects field: [end] with schema type: ["int"] but received value: [None]'
        self.assertEqual(validation_result.messages[2], expected_message_2)
        expected_message_1 = '-2147483648 <= None <= 2147483647'
        self.assertEqual(validation_result.messages[1], expected_message_1)
        expected_message_0 = 'Schema: ["int"] has type: [int] but received datum: [None]'
        self.assertEqual(validation_result.messages[0], expected_message_0)

    def test_case_insensitive_migrations(self):
        report_event = ReportEvent().migrateFromJsonDict({"DeNovoQualityScore": 5.0})
        self.assertEqual(5.0, report_event.deNovoQualityScore)

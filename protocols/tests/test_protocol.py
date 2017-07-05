from unittest import TestCase

from protocols.tests import get_valid_reported_somatic_structural_variant


class TestValidate(TestCase):

    def test_validate_debug(self):
        variant = get_valid_reported_somatic_structural_variant()
        variant.reportedStructuralVariantCancer.end = None

        # Check variant is not a valid ReportedSomaticStructuralVariants object
        self.assertFalse(variant.validate(jsonDict=variant.toJsonDict()))

        # Check the result of validation_result is False
        validation_result = variant.validate(jsonDict=variant.toJsonDict(), debug=True)
        self.assertFalse(validation_result.result)

        # Check the validation returns the expected messages
        expected_message_2 = 'Class: ReportedStructuralVariantCancer expects field: end with schema type: "int" but received value: None'
        self.assertEqual(validation_result.messages[2], expected_message_2)
        expected_message_1 = '-2147483648 <= None <= 2147483647'
        self.assertEqual(validation_result.messages[1], expected_message_1)
        expected_message_0 = 'Schema: "int" has type: int but received datum: None'
        self.assertEqual(validation_result.messages[0], expected_message_0)

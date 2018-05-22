from unittest import TestCase

from protocols.util.dependency_manager import VERSION_400
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.reports_4_0_0 import InterpretationRequestRD


class TestCaseMigration(TestCase):

    def _check_non_empty_fields(self, instance, exclusions=[]):
        """
        Checks that no field is empty, assuming empty as None, "", [] or {}
        If object has any nullable or non nullable field not filled it will raise an error.
        :type instance: protocols.protocol.ProtocolElement
        :return:
        """
        empty_values = [None, "", [], {}]
        for slot in instance.__slots__:
            attribute = instance.__getattribute__(slot)
            if slot not in exclusions:
                self.assertTrue(
                    attribute not in empty_values,
                    "Field '{}.{}' is empty!".format(instance.__class__, slot)
                )
                if instance.__class__.isEmbeddedType(slot):
                    if isinstance(attribute, list):
                        for element in attribute:
                            self._check_non_empty_fields(element, exclusions)
                    elif isinstance(attribute, dict):
                        for element in attribute.values():
                            self._check_non_empty_fields(element, exclusions)
                    else:
                        self._check_non_empty_fields(attribute, exclusions)

    def test_validation(self):
        """
        Ensures that validation fails when other object than a dict is passed
        :return:
        """
        old_instance = GenericFactoryAvro.get_factory_avro(
            InterpretationRequestRD, VERSION_400, fill_nullables=False
        ).create()
        self.assertFalse(InterpretationRequestRD.validate(old_instance))
        self.assertFalse(InterpretationRequestRD.validate("whatever"))
        self.assertFalse(InterpretationRequestRD.validate(True))
        self.assertTrue(InterpretationRequestRD.validate(old_instance.toJsonDict()))
        self.assertFalse(InterpretationRequestRD.validate(old_instance, verbose=True).result)
        self.assertFalse(InterpretationRequestRD.validate("whatever", verbose=True).result)
        self.assertFalse(InterpretationRequestRD.validate(False, verbose=True).result)
        self.assertTrue(InterpretationRequestRD.validate(old_instance.toJsonDict(), verbose=True).result)

    def test_equality(self):
        """
        Ensures that validation fails when other object than a dict is passed
        :return:
        """
        first_instance = GenericFactoryAvro.get_factory_avro(
            InterpretationRequestRD, VERSION_400, fill_nullables=False
        ).create()
        second_instance = GenericFactoryAvro.get_factory_avro(
            InterpretationRequestRD, VERSION_400, fill_nullables=False
        ).create()
        self.assertFalse(first_instance.equals(second_instance) is True)
        self.assertFalse(second_instance.equals(first_instance) is True)
        self.assertTrue(first_instance.equals(first_instance) is True)
        self.assertTrue(second_instance.equals(second_instance) is True)

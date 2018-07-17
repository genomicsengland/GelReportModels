from unittest import TestCase
from random import randint
from protocols.reports_3_0_0 import RareDiseaseExitQuestionnaire as RD_EQ_3


class TestCaseMigration(TestCase):

    bases = ["A", "C", "G", "T"]
    chromosomes = range(1, 23) + ["X"] + ["Y"]

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

    def _validate(self, instance):
        self.assertTrue(instance.validate(instance.toJsonDict(), verbose=True))

    def populate_exit_questionnaire_variant_details(self, eq):
        for vglq in eq.variantGroupLevelQuestions:
            for vlq in vglq.variantLevelQuestions:
                variant_details = "{chr}:{pos}:{ref}:{alt}".format(
                    chr=self.chromosomes[randint(0, len(self.chromosomes)-1)],
                    pos=randint(1, 10000),
                    ref=self.bases[randint(0, len(self.bases)-1)],
                    alt=self.bases[randint(0, len(self.bases)-1)],
                )
                if isinstance(eq, RD_EQ_3):
                    vlq.variant_details = variant_details
                else:
                    vlq.variantDetails = variant_details
        return eq

from random import randint
from unittest import TestCase
import logging
import dictdiffer
import random

from protocols.util import dependency_manager
from protocols.util import handle_avro_errors
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols import reports_3_0_0
from protocols.reports_3_0_0 import RareDiseaseExitQuestionnaire as RD_EQ_3


class TestCaseMigration(TestCase):

    bases = ["A", "C", "G", "T"]
    chromosomes = list(map(str, range(1, 23))) + ["X"] + ["Y"]
    version_2_1_0 = dependency_manager.VERSION_210
    version_3_0_0 = dependency_manager.VERSION_300
    version_4_0_0 = dependency_manager.VERSION_400
    version_5_0_0 = dependency_manager.VERSION_500
    version_6_1 = dependency_manager.VERSION_61
    version_7_0 = dependency_manager.VERSION_70

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

    def populate_c_eq_variant_level_questions_variant_details(self, old_c_eq):
        a = old_c_eq.somaticVariantLevelQuestions is not None
        b = old_c_eq.germlineVariantLevelQuestions is not None
        c = old_c_eq.otherActionableVariants is not None
        if a and b and c:
            combined = zip(
                old_c_eq.somaticVariantLevelQuestions,
                old_c_eq.germlineVariantLevelQuestions,
                old_c_eq.otherActionableVariants,
            )
            for somatic, germline, actionable in combined:
                somatic = self.populate_variant_level_questions_variant_details(q=somatic)
                germline = self.populate_variant_level_questions_variant_details(q=germline)
                actionable = self.populate_variant_level_questions_variant_details(q=actionable)
        return old_c_eq

    def populate_variant_level_questions_variant_details(self, q):
        variant_details = "{chr}:{pos}:{ref}:{alt}".format(
            chr=self.chromosomes[randint(0, len(self.chromosomes) - 1)],
            pos=randint(1, 10000),
            ref=self.bases[randint(0, len(self.bases) - 1)],
            alt=self.bases[randint(0, len(self.bases) - 1)],
        )
        q.variantDetails = variant_details
        return q

    @staticmethod
    def get_valid_object(object_type, version, fill_nullables=True, **kwargs):
        valid_object = GenericFactoryAvro.get_factory_avro(
            clazz=object_type,
            version=version,
            fill_nullables=fill_nullables,
        ).create(**kwargs)

        if not valid_object.validate(valid_object.toJsonDict()):
            raise ValueError(
                "Object of type: {object_type} is not valid: {results}".format(
                    object_type=object_type,
                    results=handle_avro_errors(valid_object.validate_parts()),
                )
            )
        return valid_object


class BaseTestRoundTrip(TestCaseMigration):

    # all empty values will not be considered as mismatchs
    _empty_values = [None, [], {}, ""]
    _equal_values = {
        reports_3_0_0.Sex.undetermined: reports_3_0_0.Sex.unknown
    }

    def _check_round_trip_migration(self, forward, backward, original, new_type,
                                    expect_equality=True, ignore_fields=[],
                                    forward_kwargs={}, backward_kwargs={}):

        migrated = forward(original.toJsonDict(), **forward_kwargs)
        self.assertIsInstance(migrated, new_type)
        self.assertValid(migrated)

        round_tripped = backward(migrated.toJsonDict(), **backward_kwargs)
        self.assertIsInstance(round_tripped, type(original))
        self.assertValid(round_tripped)

        differ = False
        for diff_type, field_path, values in list(dictdiffer.diff(round_tripped.toJsonDict(), original.toJsonDict())):
            if type(field_path).__name__ in ['unicode', 'str']:
                field_path = [field_path]
            if BaseTestRoundTrip.is_field_ignored(field_path, ignore_fields):
                continue
            if isinstance(values, list):
                values = values[0]
            expected = values[1]
            observed = values[0]
            if observed in self._empty_values and expected in self._empty_values:
                continue
            if self.is_hashable(expected) and self._equal_values.get(expected, "not the same") == observed:
                continue
            if expected == observed:
                continue
            logging.error("{}: {} expected '{}' found '{}'".format(diff_type, ".".join(
                list(map(str, field_path))), expected, observed))
            differ = True
        if expect_equality:
            self.assertFalse(differ)
        return round_tripped

    def is_hashable(self, item):
        try:
            hash(item)
            return True
        except:
            return False

    @staticmethod
    def is_field_ignored(field_path, ignored_fields):
        for ignored_field in ignored_fields:
            for path in field_path:
                if ignored_field in str(path):
                    return True
        return False

    def assertValid(self, instance):
        validation = instance.validate(instance.toJsonDict(), verbose=True)
        if not validation.result:
            for message in validation.messages:
                print(message)
            self.assertFalse(True)

    @staticmethod
    def _get_random_variant_details():
        reference, alternate = random.sample(['A', 'C', 'G', 'T'], 2)
        return "{chromosome}:{position}:{reference}:{alternate}".format(
            chromosome=random.randint(1, 22),
            position=random.randint(100, 1000000),
            reference=reference,
            alternate=alternate
        )

from random import randint
from unittest import TestCase
import logging
import dictdiffer
import random

from protocols.migration import BaseMigration
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
    version_7_2 = dependency_manager.VERSION_72

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
        return BaseMigration.validate_object(instance, type(instance))

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


class BaseRoundTripper(object):

    _empty_values = [None, [], {}, ""]
    _equal_values = {
        reports_3_0_0.Sex.undetermined: reports_3_0_0.Sex.unknown
    }

    def round_trip_migration(self, forward, backward, original, forward_kwargs={}, backward_kwargs={}):

        migrated = forward(original.toJsonDict(), **forward_kwargs)
        round_tripped = backward(migrated.toJsonDict(), **backward_kwargs)
        return migrated, round_tripped

    def diff_round_tripped(self, original, round_tripped, ignore_fields=[]):
        differ = False
        for diff_type, field_path, values in list(
                dictdiffer.diff(round_tripped.toJsonDict(), original.toJsonDict())):
            if type(field_path).__name__ in ['unicode', 'str']:
                field_path = [field_path]
            if self.is_field_ignored(field_path, ignore_fields):
                continue
            expected = values[1] if len(values) > 1 else None
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
        return differ

    def diff_actions(self, report_events):
        actions = {}
        # NOTE: makes the assumption that the URL field is never empty
        for re in report_events:
            if re.actions:
                for a in re.actions:
                    key = "{}-{}-{}".format(a.url if a.url else '', a.actionType, a.variantActionable)
                    if key not in actions:
                        actions[key] = []
                    actions[key].append(a)
        differ = False
        for key, a in actions.items():
            differ_pair_number = len(a) % 2 != 0
            if differ_pair_number:
                logging.error("Diff. {} number of actions for key {}".format(len(a), key))
            differ |= differ_pair_number
            if len(a) > 1:
                differ_action_type = a[0].actionType != a[1].actionType
                if differ_action_type:
                    logging.error("Diff. Action type left='{}' right='{}' for key {}".format(
                        a[0].actionType, a[1].actionType, key))
                differ |= differ_action_type
                differ_url = (a[0].url if a[0].url else None) != (a[1].url if a[1].url else None)
                if differ_url:
                    logging.error("Diff. URL left='{}' right='{}' for key {}".format(
                        a[0].url, a[1].url, key))
                differ |= differ_url
                differ_actionable = a[0].variantActionable != a[1].variantActionable
                if differ_actionable:
                    logging.error("Diff. Actionable left='{}' right='{}' for key {}".format(
                        a[0].variantActionable, a[1].variantActionable, key))
                differ |= differ_actionable
            if differ:
                logging.error("Actions differ. {}".format(a))
                break
        return differ

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


class BaseTestRoundTrip(TestCaseMigration, BaseRoundTripper):

    # all empty values will not be considered as mismatchs
    _empty_values = [None, [], {}, ""]
    _equal_values = {
        reports_3_0_0.Sex.undetermined: reports_3_0_0.Sex.unknown
    }

    def _check_round_trip_migration(self, forward, backward, original, new_type,
                                    expect_equality=True, ignore_fields=[],
                                    forward_kwargs={}, backward_kwargs={}):

        migrated, round_tripped = self.round_trip_migration(
            forward, backward, original, forward_kwargs, backward_kwargs)
        differ = self.diff_round_tripped(original, round_tripped, ignore_fields)
        self.assertIsInstance(migrated, new_type)
        self.assertValid(migrated)
        self.assertIsInstance(round_tripped, type(original))
        self.assertValid(round_tripped)
        if expect_equality:
            self.assertFalse(differ)
        return round_tripped

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

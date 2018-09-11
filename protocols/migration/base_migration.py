from __future__ import print_function
import logging

from protocols import reports_5_0_0, reports_6_0_0, reports_4_0_0
from protocols.util import handle_avro_errors
from pprint import pprint


class MigrationError(Exception):

    pass


class BaseMigration(object):

    @staticmethod
    def convert_class(target_klass, instance):
        """
        :param target_klass: type
        :param instance:
        :rtype: target_klass
        """
        new_instance = target_klass.migrateFromJsonDict(
            jsonDict=instance.toJsonDict()
        )
        return new_instance

    @staticmethod
    def validate_object(object_to_validate, object_type):
        json_dict = object_to_validate.toJsonDict()
        if object_to_validate.validate(jsonDict=json_dict):
            return object_to_validate
        else:
            pprint(handle_avro_errors(object_to_validate.validate_parts()))
            for message in object_to_validate.validate(json_dict, verbose=True).messages:
                print("---------------")
                print(message)
            raise MigrationError("New {object_type} object is not valid".format(object_type=object_type))

    @staticmethod
    def convert_string_to_integer(string, default_value=None, defaulting_message=None, fail=True):
        if string is None:
            return default_value
        try:
            return int(string)
        except ValueError:
            if default_value:
                if defaulting_message:
                    logging.warning(defaulting_message)
                return default_value
            message = "Value: {string} is not an integer contained in a string !".format(string=string)
            if fail:
                raise MigrationError(message)
            else:
                logging.warning(message)
                return None

    @staticmethod
    def convert_string_to_float(string, default_value=None, fail=True):
        if string is None:
            return default_value
        try:
            return float(string)
        except ValueError:
            if default_value:
                return default_value
            message = "Value: {string} is not a float contained in a string !".format(string=string)
            if fail:
                raise MigrationError(message)
            else:
                logging.warning(message)
                return None

    @staticmethod
    def convert_collection(things, migrate_function, default=None, **kwargs):
        if things is None:
            return default
        elif isinstance(things, (list)):
            migrated_list = [migrate_function(thing, **kwargs) for thing in things]
            return list(filter(lambda x: x is not None, migrated_list))
        elif isinstance(things, dict):
            return {k: migrate_function(v, **kwargs) for (k, v) in things.items()}
        else:
            raise MigrationError("Trying to migrate things of unsupport type {}".format(type(things)))


class BaseMigrateReports500And600(BaseMigration):
    _tier_domain_mapping = [
        (reports_5_0_0.Tier.TIER1, reports_6_0_0.Domain.DOMAIN1),
        (reports_5_0_0.Tier.TIER2, reports_6_0_0.Domain.DOMAIN2),
        (reports_5_0_0.Tier.TIER3, reports_6_0_0.Domain.DOMAIN3),
        (reports_5_0_0.Tier.TIER4, reports_6_0_0.Domain.DOMAIN4),
        (reports_5_0_0.Tier.TIER5, reports_6_0_0.Domain.NONE),
        (reports_5_0_0.Tier.NONE, reports_6_0_0.Domain.NONE)
    ]

    tier_domain_map = {k: v for k, v in _tier_domain_mapping}
    domain_tier_map = {v: k for k, v in _tier_domain_mapping}

    clinical_signicance_map = {
        reports_5_0_0.ClinicalSignificance.benign: reports_6_0_0.ClinicalSignificance.benign,
        reports_5_0_0.ClinicalSignificance.likely_benign: reports_6_0_0.ClinicalSignificance.likely_benign,
        reports_5_0_0.ClinicalSignificance.pathogenic: reports_6_0_0.ClinicalSignificance.pathogenic,
        reports_5_0_0.ClinicalSignificance.likely_pathogenic: reports_6_0_0.ClinicalSignificance.likely_pathogenic,
        reports_5_0_0.ClinicalSignificance.uncertain_significance: reports_6_0_0.ClinicalSignificance.uncertain_significance,
        reports_5_0_0.ClinicalSignificance.VUS: reports_6_0_0.ClinicalSignificance.uncertain_significance
    }

    clinical_signicance_reverse_map = {
        reports_6_0_0.ClinicalSignificance.benign: reports_5_0_0.ClinicalSignificance.benign,
        reports_6_0_0.ClinicalSignificance.likely_benign: reports_5_0_0.ClinicalSignificance.likely_benign,
        reports_6_0_0.ClinicalSignificance.pathogenic: reports_5_0_0.ClinicalSignificance.pathogenic,
        reports_6_0_0.ClinicalSignificance.likely_pathogenic: reports_5_0_0.ClinicalSignificance.likely_pathogenic,
        reports_6_0_0.ClinicalSignificance.uncertain_significance: reports_5_0_0.ClinicalSignificance.VUS
    }


class BaseMigrateReports400And500(BaseMigration):
    _feature_type_mapping = [
        (reports_4_0_0.FeatureTypes.Transcript, reports_5_0_0.GenomicEntityType.transcript),
        (reports_4_0_0.FeatureTypes.RegulatoryRegion, reports_5_0_0.GenomicEntityType.regulatory_region),
        (reports_4_0_0.FeatureTypes.Gene, reports_5_0_0.GenomicEntityType.gene)
    ]
    feature_genomic_entity_map = {k: v for k, v in _feature_type_mapping}
    genomic_entity_feature_map = {v: k for k, v in _feature_type_mapping}

    _role_in_cancer_mapping = [
        (None, None),
        (reports_4_0_0.RoleInCancer.both, reports_5_0_0.RoleInCancer.both),
        (reports_4_0_0.RoleInCancer.oncogene, reports_5_0_0.RoleInCancer.oncogene),
        (reports_4_0_0.RoleInCancer.TSG, reports_5_0_0.RoleInCancer.tumor_suppressor_gene)
    ]
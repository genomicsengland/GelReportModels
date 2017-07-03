from unittest import TestCase

from protocols.migration.migration_reports_3_0_0_to_reports_4_0_0 import MigrateReports3To4
from protocols.reports_3_0_0 import FeatureTypes as FeatureTypes_old
from protocols.reports_3_0_0 import ReportedSomaticVariants as ReportedSomaticVariants_old
from protocols.reports_3_0_0 import SomaticOrGermline
from protocols.reports_4_0_0 import AlleleOrigin
from protocols.reports_4_0_0 import FeatureTypes as FeatureTypes_new
from protocols.reports_4_0_0 import ReportedSomaticVariants as ReportedSomaticVariants_new
from protocols.tests import MockTestObject


class TestMigrateReports3To4(TestCase):

    def test_migrate_reported_somatic_variants(self):

        old_variants = MockTestObject(object_type=ReportedSomaticVariants_old).get_valid_empty_object()
        old_variants.somaticOrGermline = SomaticOrGermline.somatic
        old_variants.reportedVariantCancer.position = 1
        old_variants.reportedVariantCancer.reportEvents[0].actions[0].variantActionable = False
        old_variants.reportedVariantCancer.reportEvents[0].genomicFeatureCancer.featureType = FeatureTypes_old.Gene
        old_variants.reportedVariantCancer.reportEvents[0].soTerms = ['']
        old_variants.reportedVariantCancer.reportEvents[0].soNames = ['']

        # Check old_variants is a valid reports_3_0_0 ReportedSomaticVariants object
        self.assertTrue(old_variants.validate(jsonDict=old_variants.toJsonDict()))

        new_variants = MockTestObject(object_type=ReportedSomaticVariants_new).get_valid_empty_object()
        new_variants.reportedVariantCancer.position = 1
        new_variants.reportedVariantCancer.reportEvents[0].actions[0].variantActionable = False
        new_variants.reportedVariantCancer.reportEvents[0].genomicFeatureCancer.featureType = FeatureTypes_new.Gene
        new_variants.alleleOrigins = [AlleleOrigin.germline_variant]

        # TODO(Greg): Figure out how to make a valid participant_1_0_0 ReportedSomaticVariants object
        # Check new_variants is a valid participant_1_0_0 ReportedSomaticVariants object
        # self.assertTrue(new_variants.validate(jsonDict=new_variants.toJsonDict()))

        migrated_object = MigrateReports3To4().migrate_reported_somatic_variants(old_variants)

        # Check migrated_object is a valid participant_1_0_0 ReportedSomaticVariants object
        self.assertTrue(isinstance(migrated_object, ReportedSomaticVariants_new))
        self.assertTrue(migrated_object.validate(jsonDict=migrated_object.toJsonDict()))

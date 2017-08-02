from unittest import TestCase

from protocols.migration.migration_reports_3_0_0_to_reports_4_0_0 import MigrateReports3To4
from protocols.reports_3_0_0 import ReportEventCancer as ReportEventCancer_old
from protocols.reports_3_0_0 import ReportedSomaticVariants as ReportedSomaticVariants_old
from protocols.reports_4_0_0 import ReportEventCancer as ReportEventCancer_new
from protocols.reports_4_0_0 import ReportedSomaticVariants as ReportedSomaticVariants_new
from protocols.util import get_valid_reported_somatic_variant_3_0_0
from protocols.util import get_valid_reported_somatic_variant_4_0_0
from protocols.util.generate_mock_objects import get_valid_report_event_cancer_3_0_0


class TestMigrateReports3To4(TestCase):

    def test_migrate_reported_somatic_variants(self):

        old_variants = get_valid_reported_somatic_variant_3_0_0()

        # Check old_variants is a valid reports_3_0_0 ReportedSomaticVariants object
        self.assertTrue(isinstance(old_variants, ReportedSomaticVariants_old))
        self.assertTrue(old_variants.validate(jsonDict=old_variants.toJsonDict()))

        new_variants = get_valid_reported_somatic_variant_4_0_0()

        # Check new_variants is a valid participant_1_0_0 ReportedSomaticVariants object
        self.assertTrue(isinstance(new_variants, ReportedSomaticVariants_new))
        self.assertTrue(new_variants.validate(jsonDict=new_variants.toJsonDict()))

        migrated_object = MigrateReports3To4().migrate_reported_somatic_variants(old_variants)

        # Check migrated_object is a valid participant_1_0_0 ReportedSomaticVariants object
        self.assertTrue(isinstance(migrated_object, ReportedSomaticVariants_new))
        self.assertTrue(migrated_object.validate(jsonDict=migrated_object.toJsonDict()))

    def test_migrate_report_event_cancer(self):

        old_report_event_cancer = get_valid_report_event_cancer_3_0_0()

        # Check old_report_event_cancer is a valid reports_3_0_0.ReportEventCancer object
        self.assertTrue(isinstance(old_report_event_cancer, ReportEventCancer_old))
        self.assertTrue(old_report_event_cancer.validate(old_report_event_cancer.toJsonDict()))

        migrated_report_event_cancer = MigrateReports3To4().migrate_report_event_cancer(old_report_event_cancer)

        # Check migrated_report_event_cancer is a valid reports_4_0_0.ReportEventCancer object
        self.assertTrue(isinstance(migrated_report_event_cancer, ReportEventCancer_new))
        self.assertTrue(migrated_report_event_cancer.validate(migrated_report_event_cancer.toJsonDict()))

    def test_migrate_report_event_cancer_specific_cancer_role(self):
        """
        Checks that genomicFeatureCancer.roleInCancer is migrated if in ['oncogene', 'TSG', 'both']
        but None otherwise
        """

        for valid_cancer_role in ['oncogene', 'TSG', 'both']:
            old_report_event_cancer = get_valid_report_event_cancer_3_0_0()
            old_report_event_cancer.genomicFeatureCancer.roleInCancer = valid_cancer_role

            migrated_report_event_cancer = MigrateReports3To4().migrate_report_event_cancer(old_report_event_cancer)

            # Check migrated_report_event_cancer.genomicFeatureCancer.roleInCancer is copied across
            self.assertEqual(
                old_report_event_cancer.genomicFeatureCancer.roleInCancer,
                migrated_report_event_cancer.genomicFeatureCancer.roleInCancer,
            )
        old_report_event_cancer = get_valid_report_event_cancer_3_0_0()
        old_report_event_cancer.genomicFeatureCancer.roleInCancer = 'not an included cancer role'

        migrated_report_event_cancer = MigrateReports3To4().migrate_report_event_cancer(old_report_event_cancer)

        self.assertIsNone(migrated_report_event_cancer.genomicFeatureCancer.roleInCancer)

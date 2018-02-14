from unittest import TestCase

from protocols import reports_3_0_0
from protocols import reports_4_0_0
from protocols.util.dependency_manager import VERSION_300
from protocols.util.dependency_manager import VERSION_400
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.reports_3_0_0 import ReportEventCancer as ReportEventCancer_old
from protocols.reports_4_0_0 import ReportEventCancer as ReportEventCancer_new
from protocols.migration.migration_reports_3_0_0_to_reports_4_0_0 import MigrateReports3To4


class TestMigrateReports3To4(TestCase):

    old_model = reports_3_0_0
    new_model = reports_4_0_0

    def test_migrate_reported_somatic_variants(self):

        old_variants = GenericFactoryAvro.get_factory_avro(self.old_model.ReportedSomaticVariants, VERSION_300)()
        old_variants.somaticOrGermline = self.old_model.SomaticOrGermline.somatic

        # Check old_variants is a valid reports_3_0_0 ReportedSomaticVariants object
        self.assertTrue(isinstance(old_variants, self.old_model.ReportedSomaticVariants))
        self.assertTrue(old_variants.validate(jsonDict=old_variants.toJsonDict()))

        new_variants = GenericFactoryAvro.get_factory_avro(self.new_model.ReportedSomaticVariants, VERSION_400)()

        # Check new_variants is a valid participant_1_0_0 ReportedSomaticVariants object
        self.assertTrue(isinstance(new_variants, self.new_model.ReportedSomaticVariants))
        self.assertTrue(new_variants.validate(jsonDict=new_variants.toJsonDict()))

        migrated_object = MigrateReports3To4().migrate_reported_somatic_variants(old_variants)

        # Check migrated_object is a valid participant_1_0_0 ReportedSomaticVariants object
        self.assertTrue(isinstance(migrated_object, self.new_model.ReportedSomaticVariants))
        self.assertTrue(migrated_object.validate(jsonDict=migrated_object.toJsonDict()))

    def test_migrate_report_event_cancer(self):

        old_report_event_cancer = GenericFactoryAvro.get_factory_avro(ReportEventCancer_old, VERSION_300)()

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
            old_report_event_cancer = GenericFactoryAvro.get_factory_avro(ReportEventCancer_old, VERSION_300)()
            old_report_event_cancer.genomicFeatureCancer.roleInCancer = valid_cancer_role

            migrated_report_event_cancer = MigrateReports3To4().migrate_report_event_cancer(old_report_event_cancer)

            # Check migrated_report_event_cancer.genomicFeatureCancer.roleInCancer is copied across
            self.assertEqual(
                old_report_event_cancer.genomicFeatureCancer.roleInCancer,
                migrated_report_event_cancer.genomicFeatureCancer.roleInCancer,
            )
        old_report_event_cancer = GenericFactoryAvro.get_factory_avro(ReportEventCancer_old, VERSION_300)()
        old_report_event_cancer.genomicFeatureCancer.roleInCancer = 'not an included cancer role'

        migrated_report_event_cancer = MigrateReports3To4().migrate_report_event_cancer(old_report_event_cancer)

        self.assertIsNone(migrated_report_event_cancer.genomicFeatureCancer.roleInCancer)

    def test_migrate_interpretation_request_rd(self):
        """Also tested with real data"""
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretationRequestRD, VERSION_300, fill_nullables=False
        ).create()  # reports_3_0_0.InterpretationRequestRD
        self.assertTrue(old_instance.validate(old_instance.toJsonDict()))
        migrated_instance = MigrateReports3To4().migrate_interpretation_request_rd(old_instance=old_instance)
        self.assertTrue(migrated_instance.validate(migrated_instance.toJsonDict()))

        old_big_wigs = old_instance.bigWigs
        new_big_wigs = migrated_instance.bigWigs

        if old_big_wigs is not None:
            for old_big_wig, new_big_wig in zip(old_big_wigs, new_big_wigs):
                self.assertIsInstance(new_big_wig, self.new_model.File)
                self.assertEqual(new_big_wig.sampleId, old_big_wig.SampleId)
                self.assertEqual(new_big_wig.uriFile, old_big_wig.URIFile)
                self.assertEqual(new_big_wig.fileType, old_big_wig.fileType)
                self.assertEqual(new_big_wig.md5Sum, None)

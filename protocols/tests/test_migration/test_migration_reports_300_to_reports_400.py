from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols import reports_3_0_0
from protocols import reports_4_0_0
from protocols.util.dependency_manager import VERSION_300
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.migration.migration_reports_300_to_reports_400 import MigrateReports3To4
import protocols.reports_3_0_0


class TestMigrateReports3To4(TestCaseMigration):

    old_model = reports_3_0_0
    new_model = reports_4_0_0

    def setUp(self):
        # avoids infinite recursion in mocked data
        # now creates another factory generating values for nullable fields
        file_factory = GenericFactoryAvro.get_factory_avro(
            protocols.reports_3_0_0.File,
            VERSION_300,
            False,
            False
        )
        GenericFactoryAvro.register_factory(
            protocols.reports_3_0_0.File,
            file_factory,
            VERSION_300,
            True
        )

    def test_migrate_clinical_report_rd(self):
        """ Test passing on 186 real cases"""
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportRD, VERSION_300, fill_nullables=False
        ).create()
        self._validate(old_instance)
        migrated_instance = MigrateReports3To4().migrate_clinical_report_rd(old_instance=old_instance)
        self._validate(migrated_instance)

        # fill all nullables
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportRD, VERSION_300, fill_nullables=True
        ).create()
        self._validate(old_instance)
        migrated_instance = MigrateReports3To4().migrate_clinical_report_rd(old_instance=old_instance)
        self._validate(migrated_instance)

    def test_migrate_interpreted_genome_rd(self):
        """ Test passing on 3000 real cases"""
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_300, fill_nullables=False
        ).create()
        self._validate(old_instance)
        migrated_instance = MigrateReports3To4().migrate_interpreted_genome_rd(old_instance=old_instance)
        self._validate(migrated_instance)

        # fill all nullables
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_300, fill_nullables=True
        ).create()

        self._validate(old_instance)
        migrated_instance = MigrateReports3To4().migrate_interpreted_genome_rd(old_instance=old_instance)
        self._validate(migrated_instance)

        old_hgnc_symbols = [re.genomicFeature.HGNC for rv in old_instance.reportedVariants for re in rv.reportEvents]
        new_hgnc_symbols = [re.genomicFeature.hgnc for rv in migrated_instance.reportedVariants for re in rv.reportEvents]
        self.assertEqual(old_hgnc_symbols, new_hgnc_symbols)

    def test_migrate_interpretation_request_rd(self):
        """Also tested with real data"""
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretationRequestRD, VERSION_300, fill_nullables=False
        ).create()  # reports_3_0_0.InterpretationRequestRD
        self._validate(old_instance)
        migrated_instance = MigrateReports3To4().migrate_interpretation_request_rd(old_instance=old_instance)
        self._validate(migrated_instance)

        old_big_wigs = old_instance.bigWigs
        new_big_wigs = migrated_instance.bigWigs

        if old_big_wigs is not None:
            for old_big_wig, new_big_wig in zip(old_big_wigs, new_big_wigs):
                self.assertIsInstance(new_big_wig, self.new_model.File)
                self.assertEqual(new_big_wig.sampleId, old_big_wig.SampleId)
                self.assertEqual(new_big_wig.uriFile, old_big_wig.URIFile)
                self.assertEqual(new_big_wig.fileType, old_big_wig.fileType)
                self.assertEqual(new_big_wig.md5Sum, None)

        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretationRequestRD, VERSION_300, fill_nullables=True
        ).create()  # reports_3_0_0.InterpretationRequestRD
        self._validate(old_instance)
        migrated_instance = MigrateReports3To4().migrate_interpretation_request_rd(old_instance=old_instance)

        for old_variant, new_variant in zip(old_instance.TieredVariants, migrated_instance.tieredVariants):
            for old_re, new_re in zip(old_variant.reportEvents, new_variant.reportEvents):
                self.assertEqual(old_re.genomicFeature.HGNC, new_re.genomicFeature.hgnc)

        self._validate(migrated_instance)

    def test_migrate_reported_variants(self):

        old_ig = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_300, fill_nullables=True
        ).create()

        reported_variants_4 = MigrateReports3To4.convert_collection(
            [(v, self.new_model.ReportedVariant.fromJsonDict(v.toJsonDict()))
             for v in old_ig.reportedVariants], MigrateReports3To4()._migrate_reported_variant
        )

        old_hgnc_symbols = [re.genomicFeature.HGNC for rv in old_ig.reportedVariants for re in rv.reportEvents]
        new_hgnc_symbols = [re.genomicFeature.hgnc for rv in reported_variants_4 for re in rv.reportEvents]
        [self.assertIsNotNone(symbol) for symbol in old_hgnc_symbols]
        [self.assertIsNotNone(symbol) for symbol in new_hgnc_symbols]
        self.assertEqual(old_hgnc_symbols, new_hgnc_symbols)

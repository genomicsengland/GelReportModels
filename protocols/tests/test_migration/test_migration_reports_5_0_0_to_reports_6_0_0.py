from protocols import reports_6_0_0
from protocols import reports_5_0_0
from protocols.util.dependency_manager import VERSION_61
from protocols.util.factories.avro_factory import FactoryAvro
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_5_0_0_to_reports_6_0_0 import MigrateReports500To600


class TestMigrateInterpretedGenome5To6(TestCaseMigration):

    old_model = reports_5_0_0
    new_model = reports_6_0_0

    def test_migrate_interpreted_genome_rd(self, fill_nullables=True):
        old_ig_rd = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_61, fill_nullables=fill_nullables
        ).create()
        new_ig_rd = MigrateReports500To600().migrate_interpreted_genome_rd(old_instance=old_ig_rd)
        self._validate(new_ig_rd)
        self.assertIsInstance(new_ig_rd, self.new_model.InterpretedGenome)

        self.assertIsInstance(new_ig_rd.versionControl, self.new_model.ReportVersionControl)

        attributes = [
            "interpretationRequestId", "interpretationRequestVersion", "interpretationService", "reportUrl",
            "referenceDatabasesVersions", "softwareVersions", "comments",
        ]
        for attribute in attributes:
            if getattr(old_ig_rd, attribute) is not None:
                self.assertEqual(getattr(new_ig_rd, attribute), getattr(old_ig_rd, attribute))

        old_variants = old_ig_rd.variants
        new_variants = new_ig_rd.variants
        for old, new in zip(old_variants, new_variants):
            self.assertIsInstance(new, self.new_model.SmallVariant)
            self.assertEqual(
                new,
                MigrateReports500To600().migrate_variant(old_variant=old)
            )
        for v in new_variants:
            for re in v.reportEvents:
                if re.genePanel is not None:
                    self.assertTrue(re.genePanel.source == 'panelapp')

    def test_migrate_interpreted_genome_rd_no_nullables(self):
        self.test_migrate_interpreted_genome_rd(fill_nullables=False)

    def test_migrate_reported_variant_no_nullables(self):
        self.test_migrate_reported_variant(fill_nullables=False)

    def test_migrate_reported_variant(self, fill_nullables=True):
        old_reported_variant = GenericFactoryAvro.get_factory_avro(
            self.old_model.ReportedVariant, VERSION_61, fill_nullables=fill_nullables
        ).create()
        new_small_variant = MigrateReports500To600().migrate_variant(old_variant=old_reported_variant)
        self._validate(new_small_variant)
        self.assertIsInstance(new_small_variant, self.new_model.SmallVariant)

        for attribute in ["dbSnpId", "cosmicIds", "clinVarIds"]:
            if getattr(old_reported_variant, attribute) is not None:
                self.assertEqual(
                    getattr(old_reported_variant, attribute),
                    getattr(new_small_variant.variantAttributes.variantIdentifiers, attribute)
                )

        attributes = [
            "genomicChanges", "cdnaChanges", "proteinChanges", "additionalTextualVariantAnnotations", "references",
            "additionalNumericVariantAnnotations", "comments"
        ]
        for attribute in attributes:
            if getattr(old_reported_variant, attribute) is not None:
                self.assertEqual(
                    getattr(old_reported_variant, attribute),
                    getattr(new_small_variant.variantAttributes, attribute)
                )

        if old_reported_variant.alleleFrequencies is not None:
            old_frequencies = old_reported_variant.alleleFrequencies
            new_frequencies = new_small_variant.variantAttributes.alleleFrequencies
            for old, new in zip(old_frequencies, new_frequencies):
                self.assertIsInstance(new, self.new_model.AlleleFrequency)
                self.assertEqual(new, MigrateReports500To600().migrate_allele_frequency(old_frequency=old))

        if old_reported_variant.alleleOrigins is not None:
            old_origins = old_reported_variant.alleleOrigins
            new_origins = new_small_variant.variantAttributes.alleleOrigins
            for old, new in zip(old_origins, new_origins):
                self.assertEqual(new, old)

        old_calls = old_reported_variant.variantCalls
        new_calls = new_small_variant.variantCalls
        for old, new in zip(old_calls, new_calls):
            self.assertIsInstance(new, self.new_model.VariantCall)
            self.assertEqual(new, MigrateReports500To600().migrate_variant_call(variant_call=old))

        old_events = old_reported_variant.reportEvents
        new_events = new_small_variant.reportEvents
        for old, new in zip(old_events, new_events):
            self.assertIsInstance(new, self.new_model.ReportEvent)
            self.assertEqual(new, MigrateReports500To600().migrate_report_event(report_event=old))

        self.assertIsInstance(new_small_variant.variantAttributes, self.new_model.VariantAttributes)
        self.assertEqual(
            new_small_variant.variantAttributes,
            MigrateReports500To600().migrate_variant_attributes(old_variant=old_reported_variant)
        )

    def test_migrate_variant_call(self, fill_nullables=True):
        old_variant_call = GenericFactoryAvro.get_factory_avro(
            self.old_model.VariantCall, VERSION_61, fill_nullables=fill_nullables
        ).create()
        new_variant_call = MigrateReports500To600().migrate_variant_call(variant_call=old_variant_call)
        self._validate(new_variant_call)
        self.assertIsInstance(new_variant_call, self.new_model.VariantCall)

    def test_migrate_variant_call_no_nullables(self):
        self.test_migrate_variant_call(fill_nullables=False)

    def test_migrate_report_event(self, fill_nullables=True):
        old_report_event = GenericFactoryAvro.get_factory_avro(
            self.old_model.ReportEvent, VERSION_61, fill_nullables=fill_nullables
        ).create()
        new_report_event = MigrateReports500To600().migrate_report_event(report_event=old_report_event)
        self._validate(new_report_event)
        self.assertIsInstance(new_report_event, self.new_model.ReportEvent)

    def test_migrate_report_event_no_nullables(self):
        self.test_migrate_report_event(fill_nullables=False)

    def test_migrate_phenotypes(self):
        new_phenotypes = MigrateReports500To600().migrate_phenotypes(phenotypes=["some", "strings"])
        self._validate(new_phenotypes)
        self.assertIsInstance(new_phenotypes, self.new_model.Phenotypes)

    def test_migrate_genomic_entity(self, fill_nullables=True):
        old_genomic_entity = GenericFactoryAvro.get_factory_avro(
            self.old_model.GenomicEntity, VERSION_61, fill_nullables=fill_nullables
        ).create()
        new_genomic_entity = MigrateReports500To600().migrate_genomic_entity(genomic_entity=old_genomic_entity)
        self._validate(new_genomic_entity)
        self.assertIsInstance(new_genomic_entity, self.new_model.GenomicEntity)

    def test_migrate_genomic_entity_no_nullables(self):
        self.test_migrate_genomic_entity(fill_nullables=False)

    def test_migrate_allele_frequency(self, fill_nullables=True):
        old_allele_frequency = GenericFactoryAvro.get_factory_avro(
            self.old_model.AlleleFrequency, VERSION_61, fill_nullables=fill_nullables
        ).create()
        new_allele_frequency = MigrateReports500To600().migrate_allele_frequency(old_frequency=old_allele_frequency)
        self._validate(new_allele_frequency)
        self.assertIsInstance(new_allele_frequency, self.new_model.AlleleFrequency)

    def test_migrate_allele_frequency_no_nullables(self):
        self.test_migrate_allele_frequency(fill_nullables=False)

    def test_migrate_reported_variant_no_nullables(self):
        self.test_migrate_reported_variant(fill_nullables=False)

    def test_migrate_variant_classification(self, fill_nullables=True):
        old_variant_classification = GenericFactoryAvro.get_factory_avro(
            self.old_model.VariantClassification, VERSION_61, fill_nullables=fill_nullables
        ).create()
        new_variant_classification = MigrateReports500To600().migrate_variant_classification(
            classification=old_variant_classification
        )
        self._validate(new_variant_classification)
        self.assertIsInstance(new_variant_classification, self.new_model.VariantClassification)

    def test_migrate_variant_classification_no_nullables(self):
        self.test_migrate_variant_classification(fill_nullables=False)


class TestMigrateClinicalReport5To6(TestCaseMigration):

    old_model = reports_5_0_0
    new_model = reports_6_0_0

    def test_migrate_clinical_report_rd(self, fill_nullables=True):
        old_clinical_report_rd = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportRD, VERSION_61, fill_nullables=fill_nullables
        ).create()
        new_clinical_report = MigrateReports500To600().migrate_clinical_report_rd(
            old_instance=old_clinical_report_rd
        )
        self._validate(new_clinical_report)
        self.assertIsInstance(new_clinical_report, self.new_model.ClinicalReport)

        attributes = [
            "interpretationRequestId", "interpretationRequestVersion", "reportingDate", "user", "genomicInterpretation",
            "referenceDatabasesVersions", "softwareVersions", "references"
        ]
        for attribute in attributes:
            if getattr(old_clinical_report_rd, attribute) is not None:
                self.assertEqual(
                    getattr(old_clinical_report_rd, attribute),
                    getattr(new_clinical_report, attribute)
                )

        old_variants = old_clinical_report_rd.variants
        if old_variants is not None:
            new_variants = new_clinical_report.variants
            for old, new in zip(old_variants, new_variants):
                self.assertIsInstance(new, self.new_model.SmallVariant)
                self._validate(new)
                self.assertEqual(
                    new,
                    MigrateReports500To600().migrate_variant(old_variant=old)
                )

        if old_clinical_report_rd.additionalAnalysisPanels is not None:
            for panel in new_clinical_report.additionalAnalysisPanels:
                self.assertIsInstance(panel, self.new_model.AdditionalAnalysisPanel)

    def test_migrate_clinical_report_rd_no_nullables(self):
        self.test_migrate_clinical_report_rd(fill_nullables=False)


class TestRareDiseaseExitQuestionnaire5To6(TestCaseMigration):

    old_model = reports_5_0_0
    new_model = reports_6_0_0

    def test_migrate_rd_exit_questionnaire(self, fill_nullables=True):
        old_rd_eq = GenericFactoryAvro.get_factory_avro(
            self.old_model.RareDiseaseExitQuestionnaire, VERSION_61, fill_nullables=fill_nullables
        ).create()
        old_rd_eq = self.populate_exit_questionnaire_variant_details(eq=old_rd_eq)
        new_rd_eq = MigrateReports500To600().migrate_rd_exit_questionnaire(
            old_instance=old_rd_eq, assembly="GRCh38"
        )
        self._validate(new_rd_eq)
        self.assertIsInstance(new_rd_eq, self.new_model.RareDiseaseExitQuestionnaire)

        self.assertEqual(old_rd_eq.eventDate, new_rd_eq.eventDate)
        self.assertEqual(old_rd_eq.reporter, new_rd_eq.reporter)

        self.assertIsInstance(
            new_rd_eq.familyLevelQuestions,
            self.new_model.FamilyLevelQuestions
        )
        attributes = [
            "caseSolvedFamily", "segregationQuestion", "additionalComments"
        ]
        for attribute in attributes:
            self.assertEqual(
                getattr(old_rd_eq.familyLevelQuestions, attribute),
                getattr(new_rd_eq.familyLevelQuestions, attribute),
            )

        for VGLQ in new_rd_eq.variantGroupLevelQuestions:
            self.assertIsInstance(
                VGLQ,
                self.new_model.VariantGroupLevelQuestions
            )
            for VLQ in VGLQ.variantLevelQuestions:
                self.assertIsInstance(
                    VLQ,
                    self.new_model.VariantLevelQuestions
                )


class TestCancerInterpretedGenome5To6(TestCaseMigration):

    old_model = reports_5_0_0
    new_model = reports_6_0_0

    def test_migrate_cancer_interpreted_genome(self, fill_nullables=True):
        old_c_ig = GenericFactoryAvro.get_factory_avro(
            self.old_model.CancerInterpretedGenome, VERSION_61, fill_nullables=fill_nullables
        ).create()
        new_c_ig = MigrateReports500To600().migrate_cancer_interpreted_genome(
            old_instance=old_c_ig,
        )
        self.assertIsInstance(new_c_ig, self.new_model.InterpretedGenome)
        self._validate(new_c_ig)
        attributes = [
            "interpretationRequestId", "interpretationRequestVersion", "interpretationService", "reportUrl",
            "referenceDatabasesVersions", "softwareVersions", "comments",
        ]
        for attribute in attributes:
            if getattr(old_c_ig, attribute) is not None:
                self.assertEqual(getattr(new_c_ig, attribute), getattr(old_c_ig, attribute))
        self.assertEqual(new_c_ig.versionControl.gitVersionControl, "6.0.0")

        old_variants = old_c_ig.variants
        new_variants = new_c_ig.variants
        for old, new in zip(old_variants, new_variants):
            self.assertIsInstance(new, self.new_model.SmallVariant)
            self.assertEqual(
                new,
                MigrateReports500To600().migrate_reported_variant_cancer(variant=old)
            )

    def test_migrate_cancer_interpreted_genome_no_nullables(self):
        self.test_migrate_cancer_interpreted_genome(fill_nullables=False)

    def test_migrate_report_event_cancer(self, fill_nullables=True):
        old_re_c = GenericFactoryAvro.get_factory_avro(
            self.old_model.ReportEventCancer, VERSION_61, fill_nullables=fill_nullables
        ).create()
        new_re_c = MigrateReports500To600().migrate_report_event_cancer(
            event=old_re_c,
        )
        self.assertIsInstance(new_re_c, self.new_model.ReportEvent)
        self._validate(new_re_c)


class TestCancerClinicalReport5To6(TestCaseMigration):

    old_model = reports_5_0_0
    new_model = reports_6_0_0

    def test_migrate_cancer_clinical_report(self, fill_nullables=True):
        old_cr_c = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportCancer, VERSION_61, fill_nullables=fill_nullables
        ).create()
        new_cr_c = MigrateReports500To600().migrate_cancer_clinical_report(
            old_instance=old_cr_c,
        )
        self.assertIsInstance(new_cr_c, self.new_model.ClinicalReport)
        self._validate(new_cr_c)

from protocols import reports_6_0_0
from protocols import reports_5_0_0
from protocols.migration import BaseMigration
from protocols.util.dependency_manager import VERSION_61
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_500_to_reports_600 import MigrateReports500To600


class TestMigrateInterpretationRequest5To6(TestCaseMigration):

    old_model = reports_5_0_0
    new_model = reports_6_0_0

    def test_migrate_interpretation_request_rd(self, fill_nullables=True):
        old_ir_rd = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretationRequestRD, VERSION_61, fill_nullables=fill_nullables
        ).create()
        new_ir_rd = MigrateReports500To600().migrate_interpretation_request_rd(old_instance=old_ir_rd)
        self._validate(new_ir_rd)
        self.assertIsInstance(new_ir_rd, self.new_model.InterpretationRequestRD)
        self.assertIsInstance(new_ir_rd.versionControl, self.new_model.ReportVersionControl)
        self.assertEqual(new_ir_rd.versionControl.gitVersionControl, '6.0.0')

    def test_migrate_interpretation_request_rd_no_nullables(self):
        self.test_migrate_interpretation_request_rd(fill_nullables=False)

    def test_migrate_interpretation_request_cancer(self, fill_nullables=True):
        old_ir_cancer = GenericFactoryAvro.get_factory_avro(
            self.old_model.CancerInterpretationRequest, VERSION_61, fill_nullables=fill_nullables
        ).create()
        new_ir_cancer = MigrateReports500To600().migrate_interpretation_request_cancer(old_instance=old_ir_cancer)
        self._validate(new_ir_cancer)
        self.assertIsInstance(new_ir_cancer, self.new_model.CancerInterpretationRequest)
        self.assertIsInstance(new_ir_cancer.versionControl, self.new_model.ReportVersionControl)
        self.assertEqual(new_ir_cancer.versionControl.gitVersionControl, '6.0.0')

    def test_migrate_interpretation_request_cancer_no_nullables(self):
        self.test_migrate_interpretation_request_cancer(fill_nullables=False)


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
        self.assertEqual(new_ig_rd.versionControl.gitVersionControl, '6.0.0')

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
                MigrateReports500To600()._migrate_variant((old, new))
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
        new_small_variant = BaseMigration.convert_class(reports_6_0_0.SmallVariant, old_reported_variant)
        new_small_variant = MigrateReports500To600()._migrate_variant((old_reported_variant, new_small_variant))
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

        if old_reported_variant.alleleOrigins is not None:
            old_origins = old_reported_variant.alleleOrigins
            new_origins = new_small_variant.variantAttributes.alleleOrigins
            for old, new in zip(old_origins, new_origins):
                self.assertEqual(new, old)

        old_calls = old_reported_variant.variantCalls
        new_calls = new_small_variant.variantCalls
        for old, new in zip(old_calls, new_calls):
            self.assertIsInstance(new, self.new_model.VariantCall)
            self.assertEqual(new, MigrateReports500To600()._migrate_variant_call((old, new)))

        old_events = old_reported_variant.reportEvents
        new_events = new_small_variant.reportEvents
        for old, new in zip(old_events, new_events):
            self.assertIsInstance(new, self.new_model.ReportEvent)
            self.assertEqual(new.toJsonDict(), MigrateReports500To600()._migrate_report_event((old, new)).toJsonDict())

        self.assertIsInstance(new_small_variant.variantAttributes, self.new_model.VariantAttributes)
        self.assertEqual(
            new_small_variant.variantAttributes,
            MigrateReports500To600()._migrate_variant_attributes(old_variant=old_reported_variant)
        )

    def test_migrate_reported_variant_with_consequence(self, fill_nullables=True):
        old_reported_variant = GenericFactoryAvro.get_factory_avro(
            self.old_model.ReportedVariant, VERSION_61, fill_nullables=fill_nullables
        ).create()
        old_reported_variant.additionalTextualVariantAnnotations = {
            'ConsequenceType': "initiator_codon_variant,incomplete_terminal_codon_variant"}
        old_reported_variant.reportEvents[0].tier = self.old_model.Tier.TIER1
        old_reported_variant.reportEvents[1].tier = self.old_model.Tier.TIER2
        new_small_variant = BaseMigration.convert_class(reports_6_0_0.SmallVariant, old_reported_variant)
        new_small_variant = MigrateReports500To600()._migrate_variant((old_reported_variant, new_small_variant))
        self._validate(new_small_variant)
        self.assertIsInstance(new_small_variant, self.new_model.SmallVariant)
        self.assertEqual(len(new_small_variant.reportEvents[0].variantConsequences), 1)
        self.assertTrue(new_small_variant.reportEvents[0].variantConsequences[0].name == 'initiator_codon_variant')
        self.assertEqual(len(new_small_variant.reportEvents[1].variantConsequences), 1)
        self.assertTrue(new_small_variant.reportEvents[1].variantConsequences[0].name == 'incomplete_terminal_codon_variant')

    def test_migrate_phenotypes(self):
        new_phenotypes = MigrateReports500To600()._migrate_phenotypes(phenotypes=["some", "strings"])
        self._validate(new_phenotypes)
        self.assertIsInstance(new_phenotypes, self.new_model.Phenotypes)

    def test_migrate_small_variant(self):
        """
        Using a different approach to test_migrate_reported_variant above
        """
        old_ig = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_61, fill_nullables=True
        ).create()
        variants_6 = MigrateReports500To600().convert_collection(
            [(v, reports_6_0_0.SmallVariant.fromJsonDict(v.toJsonDict())) for v in old_ig.variants],
            MigrateReports500To600()._migrate_variant,
            panel_source='PanelApp',
        )

        old_hgnc_symbols = [ge.geneSymbol for rv in old_ig.variants for re in rv.reportEvents for ge in re.genomicEntities]
        new_hgnc_symbols = [ge.geneSymbol for rv in variants_6 for re in rv.reportEvents for ge in re.genomicEntities]
        [self.assertIsNotNone(symbol) for symbol in old_hgnc_symbols]
        [self.assertIsNotNone(symbol) for symbol in new_hgnc_symbols]
        self.assertEqual(old_hgnc_symbols, new_hgnc_symbols)


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
                    MigrateReports500To600()._migrate_variant((old, new))
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
        self.assertEqual(new_c_ig.versionControl.gitVersionControl, '6.0.0')
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
                MigrateReports500To600().migrate_variant_cancer(variant=old)
            )

    def test_migrate_cancer_interpreted_genome_no_nullables(self):
        self.test_migrate_cancer_interpreted_genome(fill_nullables=False)

    def test_migrate_actions(self):

        action1 = self.old_model.Action()
        action1.evidenceType = "Trial (glioma)"
        action1.variantActionable = True
        action1.url = "https://clinicaltrials.gov/ct2/show/NCT02639546"

        action2 = self.old_model.Action()
        action2.evidenceType = "Trial (endometrial ca)"
        action2.variantActionable = False
        action2.url = "https://clinicaltrials.gov/ct2/show/NCT02583542"

        action3 = self.old_model.Action()
        action3.evidenceType = "Therapeutic (breast ca)"
        action3.variantActionable = False
        action3.url = "https://www.mycancergenome.org/content/disease/breast-cancer/esr1"

        action4 = self.old_model.Action()
        action4.evidenceType = "Prognostic (MDS)"
        action4.variantActionable = False
        action4.url = "https://www.mycancergenome.org/content/disease/myelodysplastic-syndromes/tp53"

        action5 = self.old_model.Action()
        action5.evidenceType = "Other (MDS)"
        action5.variantActionable = False
        action5.url = "https://www.mycancergenome.org/content/disease/myelodysplastic-syndromes/tp53"

        new_actions = MigrateReports500To600()._migrate_actions([action1, action2, action3, action4])
        self.assertIsInstance(new_actions, self.new_model.Actions)
        self._validate(new_actions)
        self.assertTrue(len(new_actions.trials) == 2)
        self.assertTrue(len(new_actions.therapies) == 1)
        self.assertTrue(len(new_actions.prognosis) == 1)


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

    def test_migrate_cancer_clinical_report_no_nullables(self):
        self.test_migrate_cancer_clinical_report(fill_nullables=True)


class TestCancerExitQuestionnaire5To6(TestCaseMigration):

    old_model = reports_5_0_0
    new_model = reports_6_0_0

    def test_migrate_cancer_exit_questionnaire(self, fill_nullables=True):
        old_c_eq = GenericFactoryAvro.get_factory_avro(
            self.old_model.CancerExitQuestionnaire, VERSION_61, fill_nullables=fill_nullables
        ).create()
        old_c_eq = self.populate_c_eq_variant_level_questions_variant_details(old_c_eq=old_c_eq)
        new_c_eq = MigrateReports500To600().migrate_cancer_exit_questionnaire(
            old_instance=old_c_eq, assembly="GRCh38",
        )
        self.assertIsInstance(new_c_eq, self.new_model.CancerExitQuestionnaire)
        self._validate(new_c_eq)

    def test_migrate_cancer_exit_questionnaire_no_nullables(self):
        self.test_migrate_cancer_exit_questionnaire(fill_nullables=False)

    def test_migrate_somatic_variant_level_questions(self, fill_nullables=True):
        old_q = GenericFactoryAvro.get_factory_avro(
            self.old_model.CancerSomaticVariantLevelQuestions, VERSION_61, fill_nullables=fill_nullables
        ).create()
        old_q = self.populate_variant_level_questions_variant_details(q=old_q)
        new_q = MigrateReports500To600()._migrate_somatic_variant_level_question(
            question=old_q, assembly="GRCh38"
        )
        self.assertIsInstance(new_q, self.new_model.CancerSomaticVariantLevelQuestions)
        self._validate(new_q)

    def test_migrate_germline_variant_level_questions(self, fill_nullables=True):
        old_q = GenericFactoryAvro.get_factory_avro(
            self.old_model.CancerGermlineVariantLevelQuestions, VERSION_61, fill_nullables=fill_nullables
        ).create()
        old_q = self.populate_variant_level_questions_variant_details(q=old_q)
        new_q = MigrateReports500To600()._migrate_germline_variant_level_question(
            question=old_q, assembly="GRCh38"
        )
        self.assertIsInstance(new_q, self.new_model.CancerGermlineVariantLevelQuestions)
        self._validate(new_q)

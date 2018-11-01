from protocols.migration import MigrateReports500To600, BaseMigration
from protocols.migration.base_migration import BaseMigrateReports500And600
from protocols.protocol_6_1 import reports as new_model
from protocols.protocol_7_0 import reports as old_model
from protocols.protocol_7_0.reports import diseaseType, TissueSource
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration.migration_reports_600_to_reports_500 import MigrateReports600To500


class TestMigrateReports600To500(TestCaseMigration):

    def test_migrate_interpretation_request_rd(self, fill_nullables=True):
        ir_rd_6 = self.get_valid_object(object_type=old_model.InterpretationRequestRD, version=self.version_7_0,
                                        fill_nullables=fill_nullables)
        ir_rd_5 = MigrateReports600To500().migrate_interpretation_request_rd(old_instance=ir_rd_6)
        self.assertIsInstance(ir_rd_5, new_model.InterpretationRequestRD)
        self.assertTrue(ir_rd_5.validate(ir_rd_5.toJsonDict()))

    def test_migrate_interpretation_request_rd_nulls(self):
        self.test_migrate_interpretation_request_rd(fill_nullables=False)

    def variant_with_type_valid_in_both_models(self):
        small_variant = self.get_valid_object(object_type=old_model.SmallVariant, version=self.version_7_0)
        for re in small_variant.reportEvents:
            for ge in re.genomicEntities:
                ge.type = old_model.GenomicEntityType.intergenic
        return small_variant
    
    def test_migration_of_new_enum_values_get_set_to_none(self):
        ir_6 = self.get_valid_object(object_type=old_model.CancerInterpretationRequest, version=self.version_7_0)
        samples = ir_6.cancerParticipant.tumourSamples
        for sample in samples:
            sample.diseaseType = diseaseType.ENDOCRINE
            sample.tissueSource = TissueSource.NOT_SPECIFIED

        ir_5 = MigrateReports600To500().migrate_interpretation_request_cancer(old_instance=ir_6)

        self.assertIsInstance(ir_5, new_model.CancerInterpretationRequest)
        self.assertTrue(ir_5.validate(ir_5.toJsonDict()))

        samples = ir_5.cancerParticipant.tumourSamples
        for sample in samples:
            self.assertIsNone(sample.diseaseType)
            self.assertIsNone(sample.tissueSource)

    def test_migrate_interpreted_genome_to_interpreted_genome_rd(self):
        # Small Variants are required to migrate from InterpretedGenome version 6 to InterpretedGenomeRD version 5 as
        # Reported Variants are required in v5 so nullables must be filled
        ig_6 = self.get_valid_object(
            object_type=old_model.InterpretedGenome, version=self.version_7_0, fill_nullables=True,
        )
        ig_rd_5 = MigrateReports600To500().migrate_interpreted_genome_to_interpreted_genome_rd(old_instance=ig_6)
        self.assertIsInstance(ig_rd_5, new_model.InterpretedGenomeRD)
        self.assertTrue(ig_rd_5.validate(ig_rd_5.toJsonDict()))

    def test_migrate_clinical_report_rd(self, fill_nullables=True):
        cr_rd_6 = self.get_valid_object(object_type=old_model.ClinicalReport, version=self.version_7_0, fill_nullables=fill_nullables)
        cr_rd_5 = MigrateReports600To500().migrate_clinical_report_rd(old_instance=cr_rd_6)
        self.assertIsInstance(cr_rd_5, new_model.ClinicalReportRD)
        self.assertTrue(cr_rd_5.validate(cr_rd_5.toJsonDict()))

    def test_migrate_clinical_report_rd_no_nullables(self):
        self.test_migrate_clinical_report_rd(fill_nullables=False)

    def test_migrate_clinical_report_cancer(self, fill_nullables=True):
        cr_6 = self.get_valid_object(object_type=old_model.ClinicalReport, version=self.version_7_0, fill_nullables=fill_nullables)
        cr_c_5 = MigrateReports600To500().migrate_clinical_report_cancer(old_instance=cr_6)
        self.assertIsInstance(cr_c_5, new_model.ClinicalReportCancer)
        self.assertTrue(cr_c_5.validate(cr_c_5.toJsonDict()))

    def test_migrate_clinical_report_cancer_no_nullables(self):
        self.test_migrate_clinical_report_cancer(fill_nullables=False)

    def test_migrate_exit_questionnaire_rd(self, fill_nullables=True):
        eq_rd_6 = self.get_valid_object(object_type=old_model.RareDiseaseExitQuestionnaire, version=self.version_7_0,
                                        fill_nullables=fill_nullables)
        eq_rd_5 = MigrateReports600To500().migrate_exit_questionnaire_rd(old_instance=eq_rd_6)
        self.assertIsInstance(eq_rd_5, new_model.RareDiseaseExitQuestionnaire)
        self.assertTrue(eq_rd_5.validate(eq_rd_5.toJsonDict()))
        self._check_variant_details_conversion(
            [vq for gq in eq_rd_6.variantGroupLevelQuestions for vq in gq.variantLevelQuestions],
            [vq for gq in eq_rd_5.variantGroupLevelQuestions for vq in gq.variantLevelQuestions])

    def test_migrate_exit_questionnaire_rd_no_nullables(self):
        self.test_migrate_exit_questionnaire_rd(fill_nullables=False)

    def test_migrate_cancer_exit_questionnaire(self, fill_nullables=True):
        ceq_6 = self.get_valid_object(object_type=old_model.CancerExitQuestionnaire, version=self.version_7_0, fill_nullables=fill_nullables)
        ceq_5 = MigrateReports600To500().migrate_cancer_exit_questionnaire(old_instance=ceq_6)
        self.assertIsInstance(ceq_5, new_model.CancerExitQuestionnaire)
        self.assertTrue(ceq_5.validate(ceq_5.toJsonDict()))
        self._check_variant_details_conversion(ceq_6.somaticVariantLevelQuestions, ceq_5.somaticVariantLevelQuestions)
        self._check_variant_details_conversion(ceq_6.germlineVariantLevelQuestions, ceq_5.germlineVariantLevelQuestions)
        self._check_variant_details_conversion(ceq_6.otherActionableVariants, ceq_5.otherActionableVariants)

    def _check_variant_details_conversion(self, things_with_coordinates, things_with_details):
        if things_with_details and things_with_coordinates:
            coordinates = [sq.variantCoordinates for sq in things_with_coordinates]
            details = [sq.variantDetails for sq in things_with_details]
            for c, d in zip(coordinates, details):
                d_fields = d.split(":")
                self.assertEqual(d_fields[0], c.chromosome)
                self.assertEqual(d_fields[1], str(c.position))
                self.assertEqual(d_fields[2], c.reference)
                self.assertEqual(d_fields[3], c.alternate)

    def test_migrate_cancer_exit_questionnaire_no_nullables(self):
        self.test_migrate_cancer_exit_questionnaire(fill_nullables=False)

    def test_migrate_report_event(self, fill_nullables=True):
        re_rd_6 = self.get_valid_object(object_type=old_model.ReportEvent, version=self.version_7_0,
                                        fill_nullables=fill_nullables)
        re_rd_6.eventJustification = None
        re_rd_6.segregationPattern = old_model.SegregationPattern.CompoundHeterozygous
        re_rd_5 = BaseMigration.convert_class(target_klass=new_model.ReportEvent, instance=re_rd_6)
        re_rd_5 = MigrateReports600To500()._migrate_report_event((re_rd_6, re_rd_5))
        self.assertIsInstance(re_rd_5, new_model.ReportEvent)
        self.assertTrue(re_rd_5.validate(re_rd_5.toJsonDict()))
        self.assertTrue(old_model.SegregationPattern.CompoundHeterozygous in re_rd_5.eventJustification)

        re_rd_6 = self.get_valid_object(object_type=old_model.ReportEvent, version=self.version_7_0,
                                        fill_nullables=fill_nullables)
        re_rd_6.eventJustification = "I have an event justification"
        re_rd_6.segregationPattern = old_model.SegregationPattern.CompoundHeterozygous
        re_rd_5 = BaseMigration.convert_class(target_klass=new_model.ReportEvent, instance=re_rd_6)
        re_rd_5 = MigrateReports600To500()._migrate_report_event((re_rd_6, re_rd_5))
        self.assertIsInstance(re_rd_5, new_model.ReportEvent)
        self.assertTrue(re_rd_5.validate(re_rd_5.toJsonDict()))
        self.assertTrue(re_rd_5.eventJustification is not None)
        self.assertTrue(old_model.SegregationPattern.CompoundHeterozygous not in re_rd_5.eventJustification)

        re_rd_6 = self.get_valid_object(object_type=old_model.ReportEvent, version=self.version_7_0,
                                        fill_nullables=fill_nullables)
        re_rd_6.eventJustification = None
        re_rd_6.segregationPattern = None
        re_rd_5 = BaseMigration.convert_class(target_klass=new_model.ReportEvent, instance=re_rd_6)
        re_rd_5 = MigrateReports600To500()._migrate_report_event((re_rd_6, re_rd_5))
        self.assertIsInstance(re_rd_5, new_model.ReportEvent)
        self.assertTrue(re_rd_5.validate(re_rd_5.toJsonDict()))
        self.assertTrue(re_rd_5.eventJustification is None)

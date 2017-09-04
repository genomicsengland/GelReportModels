from unittest import TestCase

from protocols.migration import MigrateReports3To420SNAPSHOT
from protocols import reports_4_2_0_SNAPSHOT
from protocols import reports_3_0_0
from protocols import util


class TestMigrateReports3To420SNAPSHOT(TestCase):

    old_model = reports_3_0_0
    new_model = reports_4_2_0_SNAPSHOT

    def test_migrate_interpretation_request_rd(self):

        old_interpretation_request_rd = util.get_valid_interpretation_request_rd_3_0_0()

        test_ir_id = 'CHF-2003'
        old_interpretation_request_rd.InterpretationRequestID = test_ir_id

        # Check old_interpretation_request_rd is a valid reports_3_0_0 InterpretationRequestRD object
        self.assertTrue(isinstance(old_interpretation_request_rd, self.old_model.InterpretationRequestRD))
        self.assertTrue(old_interpretation_request_rd.validate(jsonDict=old_interpretation_request_rd.toJsonDict()))

        migrated_object = MigrateReports3To420SNAPSHOT().migrate_interpretation_request_rd(
            old_interpretation_request_rd=old_interpretation_request_rd
        )

        # Check migrated_object is a valid reports_4_2_0_SNAPSHOT InterpretationRequestRD object
        self.assertTrue(isinstance(migrated_object, self.new_model.InterpretationRequestRD))
        self.assertTrue(migrated_object.validate(jsonDict=migrated_object.toJsonDict()))

        # Check version control field is now a ReportVersionControl object and has the correct details
        self.assertTrue(isinstance(migrated_object.versionControl, self.new_model.ReportVersionControl))
        self.assertDictEqual(migrated_object.versionControl.toJsonDict(), {u'gitVersionControl': '4.2.0'})

        # Check old InterpretationRequestID is migrated to new interpretationRequestId field
        self.assertEqual(migrated_object.interpretationRequestId, test_ir_id)

        # Check genomic feature is migrated correctly
        old_variants = old_interpretation_request_rd.TieredVariants
        new_variants = migrated_object.tieredVariants
        for old_variant, new_variant in zip(old_variants, new_variants):
            old_events = old_variant.reportEvents
            new_events = new_variant.reportEvents
            for old_event, new_event in zip(old_events, new_events):

                self.assertIsInstance(new_event.genomicFeature, self.new_model.GenomicFeature)

                self.assertEqual(old_event.genomicFeature.featureType, new_event.genomicFeature.featureType)
                self.assertEqual(old_event.genomicFeature.ensemblId, new_event.genomicFeature.ensemblId)
                self.assertEqual(old_event.genomicFeature.HGNC, new_event.genomicFeature.hgnc)
                self.assertEqual(old_event.genomicFeature.other_ids, new_event.genomicFeature.otherIds)

    def test_migrate_interpreted_genome_rd(self):

        old_interpreted_genome_rd = util.get_valid_interpreted_genome_rd_3_0_0()

        # Check old_interpretation_request_rd is a valid reports_3_0_0 InterpretedGenomeRD object
        self.assertTrue(isinstance(old_interpreted_genome_rd, self.old_model.InterpretedGenomeRD))
        self.assertTrue(old_interpreted_genome_rd.validate(jsonDict=old_interpreted_genome_rd.toJsonDict()))

        migrated_object = MigrateReports3To420SNAPSHOT().migrate_interpreted_genome_rd(
            old_interpreted_genome_rd=old_interpreted_genome_rd
        )

        # Check migrated_object is a valid reports_4_2_0_SNAPSHOT InterpretedGenomeRD object
        self.assertTrue(isinstance(migrated_object, self.new_model.InterpretedGenomeRD))
        self.assertTrue(migrated_object.validate(jsonDict=migrated_object.toJsonDict()))

    def test_migrate_reported_structural_variant(self):

        old_reported_structural_variant = util.get_valid_reported_structural_variant_3_0_0()

        # Check old_reported_structural_variant is a valid reports_3_0_0 ReportedStructuralVariant object
        self.assertTrue(isinstance(old_reported_structural_variant, self.old_model.ReportedStructuralVariant))
        self.assertTrue(old_reported_structural_variant.validate(jsonDict=old_reported_structural_variant.toJsonDict()))

        migrated_object = MigrateReports3To420SNAPSHOT().migrate_reported_structural_variant(
            old_reported_structural_variant=old_reported_structural_variant
        )

        # Check migrated_object is a valid reports_4_2_0_SNAPSHOT ReportedStructuralVariant object
        self.assertTrue(isinstance(migrated_object, self.new_model.ReportedStructuralVariant))
        self.assertTrue(migrated_object.validate(jsonDict=migrated_object.toJsonDict()))

from unittest import TestCase

from protocols.migration import MigrateReports3To420
from protocols import reports_4_2_0
from protocols import reports_3_0_0
from protocols import util


class TestMigrateReports3To420(TestCase):

    old_model = reports_3_0_0
    new_model = reports_4_2_0

    def test_migrate_interpretation_request_rd(self):

        old_interpretation_request_rd = util.get_valid_interpretation_request_rd_3_0_0()

        test_ir_id = 'CHF-2003'
        old_interpretation_request_rd.InterpretationRequestID = test_ir_id
        old_interpretation_request_rd.additionalInfo = {"additional": "info"}
        old_interpretation_request_rd.analysisVersion = '234'
        old_interpretation_request_rd.complexGeneticPhenomena = self.old_model.ComplexGeneticPhenomena.other_aneuploidy

        old_interpretation_request_rd.pedigree.participants[0].affectionStatus = self.old_model.AffectionStatus.unknown

        # Check old_interpretation_request_rd is a valid reports_3_0_0 InterpretationRequestRD object
        self.assertTrue(isinstance(old_interpretation_request_rd, self.old_model.InterpretationRequestRD))
        self.assertTrue(old_interpretation_request_rd.validate(jsonDict=old_interpretation_request_rd.toJsonDict()))

        migrated_object = MigrateReports3To420().migrate_interpretation_request_rd(
            old_interpretation_request_rd=old_interpretation_request_rd
        )

        # Check migrated_object is a valid reports_4_2_0 InterpretationRequestRD object
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

        self.assertIsNotNone(migrated_object.genomeAssemblyVersion)
        self.assertEqual(migrated_object.genomeAssemblyVersion, old_interpretation_request_rd.genomeAssemblyVersion)

        self.assertIsNotNone(migrated_object.cellbaseVersion)
        self.assertEqual(migrated_object.cellbaseVersion, old_interpretation_request_rd.cellbaseVersion)

        self.assertIsNotNone(migrated_object.interpretationRequestVersion)
        self.assertEqual(migrated_object.interpretationRequestVersion, old_interpretation_request_rd.InterpretationRequestVersion)

        self.assertIsNotNone(migrated_object.interpretGenome)
        self.assertEqual(migrated_object.interpretGenome, old_interpretation_request_rd.interpretGenome)

        self.assertIsNotNone(migrated_object.workspace)
        self.assertEqual(migrated_object.workspace, old_interpretation_request_rd.workspace)

        self.assertIsNotNone(migrated_object.tieringVersion)
        self.assertEqual(migrated_object.tieringVersion, old_interpretation_request_rd.TieringVersion)

        self.assertIsNotNone(migrated_object.analysisVersion)
        self.assertEqual(migrated_object.analysisReturnUri, old_interpretation_request_rd.analysisReturnURI)

        self.assertIsNotNone(migrated_object.analysisVersion)
        self.assertEqual(migrated_object.analysisVersion, old_interpretation_request_rd.analysisVersion)

        self.assertIsNotNone(migrated_object.additionalInfo)
        self.assertEqual(migrated_object.additionalInfo, old_interpretation_request_rd.additionalInfo)

        self.assertIsNotNone(migrated_object.complexGeneticPhenomena)
        self.assertEqual(migrated_object.complexGeneticPhenomena, old_interpretation_request_rd.complexGeneticPhenomena)

        self.assertIsInstance(migrated_object.otherFamilyHistory, self.new_model.OtherFamilyHistory)
        self.assertEqual(migrated_object.otherFamilyHistory.maternalFamilyHistory, old_interpretation_request_rd.otherFamilyHistory.maternalFamilyHistory)
        self.assertEqual(migrated_object.otherFamilyHistory.paternalFamilyHistory, old_interpretation_request_rd.otherFamilyHistory.paternalFamilyHistory)

        # Check BAM locations are migrated correctly
        old_bams = old_interpretation_request_rd.BAMs
        new_bams = migrated_object.bams
        for old_bam, new_bam in zip(old_bams, new_bams):
            self.assertIsInstance(new_bam, self.new_model.File)

            self.assertEqual(new_bam.sampleId, old_bam.SampleId)
            self.assertEqual(new_bam.uriFile, old_bam.URIFile)
            self.assertEqual(new_bam.fileType, old_bam.fileType)
            self.assertEqual(new_bam.md5Sum, old_bam.md5Sum)

        # Check VCF locations are migrated correctly
        old_vcfs = old_interpretation_request_rd.VCFs
        new_vcfs = migrated_object.vcfs
        for old_vcf, new_vcf in zip(old_vcfs, new_vcfs):
            self.assertIsInstance(new_vcf, self.new_model.File)

            self.assertEqual(new_vcf.sampleId, old_vcf.SampleId)
            self.assertEqual(new_vcf.uriFile, old_vcf.URIFile)
            self.assertEqual(new_vcf.fileType, old_vcf.fileType)
            self.assertEqual(new_vcf.md5Sum, old_vcf.md5Sum)

        # Check BigWig locations are migrated correctly
        old_big_wigs = old_interpretation_request_rd.bigWigs
        new_big_wigs = migrated_object.bigWigs
        for old_big_wig, new_big_wig in zip(old_big_wigs, new_big_wigs):
            self.assertIsInstance(new_big_wig, self.new_model.File)

            self.assertEqual(new_big_wig.sampleId, old_big_wig.SampleId)
            self.assertEqual(new_big_wig.uriFile, old_big_wig.URIFile)
            self.assertEqual(new_big_wig.fileType, old_big_wig.fileType)
            self.assertEqual(new_big_wig.md5Sum, old_big_wig.md5Sum)

        # Check Pedigree Diagram file is migrated correctly
        old_pedigree_diagram = old_interpretation_request_rd.pedigreeDiagram
        new_pedigree_diagram = migrated_object.pedigreeDiagram

        self.assertIsInstance(new_pedigree_diagram, self.new_model.File)

        self.assertEqual(new_pedigree_diagram.sampleId, old_pedigree_diagram.SampleId)
        self.assertEqual(new_pedigree_diagram.uriFile, old_pedigree_diagram.URIFile)
        self.assertEqual(new_pedigree_diagram.fileType, old_pedigree_diagram.fileType)
        self.assertEqual(new_pedigree_diagram.md5Sum, old_pedigree_diagram.md5Sum)

        # Check Annotation File file is migrated correctly
        old_annotation_file = old_interpretation_request_rd.annotationFile
        new_annotation_file = migrated_object.annotationFile

        self.assertIsInstance(new_annotation_file, self.new_model.File)

        self.assertEqual(new_annotation_file.sampleId, old_annotation_file.SampleId)
        self.assertEqual(new_annotation_file.uriFile, old_annotation_file.URIFile)
        self.assertEqual(new_annotation_file.fileType, old_annotation_file.fileType)
        self.assertEqual(new_annotation_file.md5Sum, old_annotation_file.md5Sum)

    def test_migrate_interpreted_genome_rd(self):

        old_interpreted_genome_rd = util.get_valid_interpreted_genome_rd_3_0_0()

        # Check old_interpretation_request_rd is a valid reports_3_0_0 InterpretedGenomeRD object
        self.assertTrue(isinstance(old_interpreted_genome_rd, self.old_model.InterpretedGenomeRD))
        self.assertTrue(old_interpreted_genome_rd.validate(jsonDict=old_interpreted_genome_rd.toJsonDict()))

        migrated_object = MigrateReports3To420().migrate_interpreted_genome_rd(
            old_interpreted_genome_rd=old_interpreted_genome_rd
        )

        # Check migrated_object is a valid reports_4_2_0 InterpretedGenomeRD object
        self.assertTrue(isinstance(migrated_object, self.new_model.InterpretedGenomeRD))
        self.assertTrue(migrated_object.validate(jsonDict=migrated_object.toJsonDict()))

    def test_migrate_reported_structural_variant(self):

        old_reported_structural_variant = util.get_valid_reported_structural_variant_3_0_0()

        # Check old_reported_structural_variant is a valid reports_3_0_0 ReportedStructuralVariant object
        self.assertTrue(isinstance(old_reported_structural_variant, self.old_model.ReportedStructuralVariant))
        self.assertTrue(old_reported_structural_variant.validate(jsonDict=old_reported_structural_variant.toJsonDict()))

        migrated_object = MigrateReports3To420().migrate_reported_structural_variant(
            old_reported_structural_variant=old_reported_structural_variant
        )

        # Check migrated_object is a valid reports_4_2_0 ReportedStructuralVariant object
        self.assertTrue(isinstance(migrated_object, self.new_model.ReportedStructuralVariant))
        self.assertTrue(migrated_object.validate(jsonDict=migrated_object.toJsonDict()))

    def test_migrate_clinical_report_rd(self):

        old_clinical_report_rd = util.get_valid_clinical_report_rd_3_0_0()

        # Check old_clinical_report_rd is a valid reports_3_0_0 ClinicalReportRD object
        self.assertTrue(isinstance(old_clinical_report_rd, self.old_model.ClinicalReportRD))
        self.assertTrue(old_clinical_report_rd.validate(jsonDict=old_clinical_report_rd.toJsonDict()))

        migrated_object = MigrateReports3To420().migrate_clinical_report_rd(
            old_clinical_report_rd=old_clinical_report_rd
        )

        # Check migrated_object is a valid reports_4_2_0 ClinicalReportRD object
        self.assertTrue(isinstance(migrated_object, self.new_model.ClinicalReportRD))
        self.assertTrue(migrated_object.validate(jsonDict=migrated_object.toJsonDict()))

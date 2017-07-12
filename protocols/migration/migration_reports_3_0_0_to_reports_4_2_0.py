from protocols import reports_3_0_0
from protocols import reports_4_2_0
from protocols.util import handle_avro_errors
from protocols.migration import BaseMigration
from protocols.migration.participants import MigrationReportsToParticipants1
from protocols.migration.participants import MigrationParticipants100To103


class MigrateReports3To420(BaseMigration):

    old_model = reports_3_0_0
    new_model = reports_4_2_0

    def migrate_interpretation_request_rd(self, old_interpretation_request_rd):
        """
        :type old_interpretation_request_rd: reports_3_0_0.InterpretationRequestRD
        :rtype: reports_4_2_0.InterpretationRequestRD
        """
        new_interpretation_request = self.new_model.InterpretationRequestRD.fromJsonDict(
            jsonDict=old_interpretation_request_rd.toJsonDict()
        )

        for participant in old_interpretation_request_rd.pedigree.participants:
            if participant.samples is None:
                participant.samples = []

        migrated_pedigree_1_0_1 = MigrationReportsToParticipants1().migrate_pedigree(pedigree=old_interpretation_request_rd.pedigree)
        migrated_pedigree = MigrationParticipants100To103().migrate_pedigree(old_pedigree=migrated_pedigree_1_0_1)

        new_interpretation_request.pedigree = reports_4_2_0.Pedigree.fromJsonDict(migrated_pedigree.toJsonDict())

        new_interpretation_request.interpretationRequestVersion = old_interpretation_request_rd.InterpretationRequestVersion
        new_interpretation_request.interpretationRequestId = old_interpretation_request_rd.InterpretationRequestID
        new_interpretation_request.tieringVersion = old_interpretation_request_rd.TieringVersion
        new_interpretation_request.tieredVariants = self.migrate_reported_variants(old_reported_variants=old_interpretation_request_rd.TieredVariants)
        new_interpretation_request.bams = self.migrate_files(old_files=old_interpretation_request_rd.BAMs)
        new_interpretation_request.vcfs = self.migrate_files(old_files=old_interpretation_request_rd.VCFs)
        new_interpretation_request.bigWigs = self.migrate_files(old_files=old_interpretation_request_rd.bigWigs)
        new_interpretation_request.otherFiles = self.migrate_files(old_files=old_interpretation_request_rd.otherFiles)
        new_interpretation_request.pedigreeDiagram = self.migrate_file(old_file=old_interpretation_request_rd.pedigreeDiagram)
        new_interpretation_request.annotationFile = self.migrate_file(old_file=old_interpretation_request_rd.annotationFile)
        new_interpretation_request.analysisReturnUri = old_interpretation_request_rd.analysisReturnURI
        new_interpretation_request.internalStudyId = ''

        new_interpretation_request.versionControl = self.new_model.ReportVersionControl()

        return self.validate_object(
            object_to_validate=new_interpretation_request, object_type=self.new_model.InterpretationRequestRD
        )

    def migrate_interpreted_genome_rd(self, old_interpreted_genome_rd):
        """
        :type old_interpreted_genome_rd: reports_3_0_0.InterpretedGenomeRD
        :rtype: reports_4_2_0.InterpretedGenomeRD
        """
        new_interpreted_genome_rd = self.new_model.InterpretedGenomeRD.fromJsonDict(
            jsonDict=old_interpreted_genome_rd.toJsonDict()
        )

        new_interpreted_genome_rd.interpretationRequestId = old_interpreted_genome_rd.InterpretationRequestID
        new_interpreted_genome_rd.reportUrl = old_interpreted_genome_rd.reportURL
        new_interpreted_genome_rd.reportUri = old_interpreted_genome_rd.reportURI

        new_interpreted_genome_rd.reportedVariants = self.migrate_reported_variants(
            old_reported_variants=old_interpreted_genome_rd.reportedVariants
        )

        new_interpreted_genome_rd.reportedStructuralVariants = self.migrate_reported_structural_variants(
            old_reported_structural_variants=old_interpreted_genome_rd.reportedStructuralVariants
        )

        return self.validate_object(
            object_to_validate=new_interpreted_genome_rd, object_type=self.new_model.InterpretedGenomeRD
        )

    def migrate_clinical_report_rd(self, old_clinical_report_rd):
        """
        :type old_clinical_report_rd: reports_3_0_0.ClinicalReportRD
        :rtype: reports_4_2_0.ClinicalReportRD
        """
        new_clinical_report_rd = self.new_model.ClinicalReportRD.fromJsonDict(
            jsonDict=old_clinical_report_rd.toJsonDict()
        )

        new_clinical_report_rd.interpretationRequestId = old_clinical_report_rd.interpretationRequestID

        if old_clinical_report_rd.candidateVariants is not None:
            new_clinical_report_rd.candidateVariants = self.migrate_reported_variants(
                old_reported_variants=old_clinical_report_rd.candidateVariants
            )
        else:
            new_clinical_report_rd.candidateVariants = None

        new_clinical_report_rd.candidateStructuralVariants = self.migrate_reported_structural_variants(
            old_reported_structural_variants=old_clinical_report_rd.candidateStructuralVariants
        )

        return self.validate_object(
            object_to_validate=new_clinical_report_rd, object_type=self.new_model.InterpretedGenomeRD
        )

    def migrate_report_event(self, old_report_event):
        new_report_event = self.new_model.ReportEvent.fromJsonDict(old_report_event.toJsonDict())
        old_classification = self.old_model.VariantClassification
        new_classification = self.new_model.VariantClassification
        variant_classification_map = {
            old_classification.PATHOGENIC: new_classification.pathogenic_variant,
            old_classification.LIKELY_PATHOGENIC: new_classification.likely_pathogenic_variant,
            old_classification.VUS: new_classification.variant_of_unknown_clinical_significance,
            old_classification.LIKELY_BENIGN: new_classification.likely_benign_variant,
            old_classification.BENIGN: new_classification.benign_variant,
        }
        new_report_event.variantClassification = variant_classification_map.get(
            old_report_event.variantClassification, new_classification.not_assessed
        )

        new_report_event.genomicFeature = self.migrate_genomic_feature(old_genomic_feature=old_report_event.genomicFeature)

        return self.validate_object(object_to_validate=new_report_event, object_type=self.new_model.ReportEvent)

    def migrate_genomic_feature(self, old_genomic_feature):
        new_genomic_feature = self.new_model.GenomicFeature()
        new_genomic_feature.featureType = old_genomic_feature.featureType
        new_genomic_feature.ensemblId = old_genomic_feature.ensemblId
        new_genomic_feature.hgnc = old_genomic_feature.HGNC
        new_genomic_feature.otherIds = old_genomic_feature.other_ids

        return self.validate_object(object_to_validate=new_genomic_feature, object_type=self.new_model.GenomicFeature)

    def migrate_report_events(self, old_report_events):
        return [self.migrate_report_event(old_report_event) for old_report_event in old_report_events]

    def migrate_reported_variant(self, old_reported_variant):
        new_tiered_variant = self.new_model.ReportedVariant.fromJsonDict(old_reported_variant.toJsonDict())
        new_tiered_variant.dbSnpId = old_reported_variant.dbSNPid
        new_tiered_variant.reportEvents = self.migrate_report_events(
            old_report_events=old_reported_variant.reportEvents
        )

        if new_tiered_variant.validate(new_tiered_variant.toJsonDict()):
            return new_tiered_variant
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(new_tiered_variant.validate_parts())
            )

    def migrate_reported_variants(self, old_reported_variants):
        return [
            self.migrate_reported_variant(
                old_reported_variant=old_reported_variant
            ) for old_reported_variant in old_reported_variants
        ]

    def migrate_reported_structural_variant(self, old_reported_structural_variant):
        new_reported_structural_variant = self.new_model.ReportedStructuralVariant.fromJsonDict(
            old_reported_structural_variant.toJsonDict()
        )
        new_reported_structural_variant.reportEvents = self.migrate_report_events(
            old_report_events=old_reported_structural_variant.reportEvents
        )

        return self.validate_object(
            object_to_validate=new_reported_structural_variant, object_type=self.new_model.ReportedStructuralVariant
        )

    def migrate_reported_structural_variants(self, old_reported_structural_variants):
        if old_reported_structural_variants is None:
            return None
        return [
            self.migrate_reported_structural_variant(
                old_reported_structural_variant=old_reported_structural_variant
            ) for old_reported_structural_variant in old_reported_structural_variants
        ]

    def migrate_file(self, old_file):
        if old_file is None:
            return None
        if isinstance(old_file.SampleId, list):
            sampleId = old_file.SampleId
        elif old_file.SampleId is None:
            sampleId = None
        else:
            sampleId = [old_file.SampleId]
        new_file = self.new_model.File(
                fileType=old_file.fileType,
                uriFile=old_file.URIFile,
                sampleId=sampleId,
                md5Sum=None,
            )
        if new_file.validate(new_file.toJsonDict()):
            return new_file
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(new_file.validate_parts()), new_file.validate(new_file.toJsonDict(), verbose=True).messages
            )

    def migrate_files(self, old_files):
        if old_files is None:
            return None
        return [self.migrate_file(old_file=old_file) for old_file in old_files]

    def migrate_life_status(self, life_status):
        life_status_map = {
            self.old_model.LifeStatus.alive: self.new_model.LifeStatus.ALIVE,
            self.old_model.LifeStatus.aborted: self.new_model.LifeStatus.ABORTED,
            self.old_model.LifeStatus.deceased: self.new_model.LifeStatus.DECEASED,
            self.old_model.LifeStatus.unborn: self.new_model.LifeStatus.UNBORN,
            self.old_model.LifeStatus.stillborn: self.new_model.LifeStatus.STILLBORN,
            self.old_model.LifeStatus.miscarriage: self.new_model.LifeStatus.MISCARRIAGE,
        }
        migrated_life_status = life_status_map.get(life_status)
        if migrated_life_status is None:
            raise ValueError(
                "Life status: [{life_status}] is not a valid life status for {object_type}".format(
                    life_status=life_status, object_type=self.old_model.LifeStatus
                )
            )

        if migrated_life_status.validate(migrated_life_status.toJsonDict()):
            return migrated_life_status
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(migrated_life_status.validate_parts())
            )

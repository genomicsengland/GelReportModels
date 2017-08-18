from protocols import reports_3_0_0
from protocols import reports_4_2_0_SNAPSHOT
from protocols.util import handle_avro_errors
from protocols.migration.participants import MigrationReportsToParticipants1
from protocols.migration.participants import MigrationParticipants100To103SNAPSHOT


class MigrateReports3To420SNAPSHOT(object):
    old_model = reports_3_0_0
    new_model = reports_4_2_0_SNAPSHOT

    def migrate_interpretation_request_rd(self, old_interpretation_request_rd):
        """
        :type old_interpretation_request_rd: reports_3_0_0.InterpretationRequestRD
        :rtype: reports_4_2_0_SNAPSHOT.InterpretationRequestRD
        """
        new_interpretation_request = self.new_model.InterpretationRequestRD.fromJsonDict(
            jsonDict=old_interpretation_request_rd.toJsonDict()
        )

        for participant in old_interpretation_request_rd.pedigree.participants:
            if participant.samples is None:
                participant.samples = []

        migrated_pedigree_1_0_1 = MigrationReportsToParticipants1().migrate_pedigree(pedigree=old_interpretation_request_rd.pedigree)
        migrated_pedigree = MigrationParticipants100To103SNAPSHOT().migrate_pedigree(old_pedigree=migrated_pedigree_1_0_1)

        new_interpretation_request.pedigree = reports_4_2_0_SNAPSHOT.Pedigree.fromJsonDict(migrated_pedigree.toJsonDict())

        new_interpretation_request.interpretationRequestVersion = old_interpretation_request_rd.InterpretationRequestVersion
        new_interpretation_request.interpretationRequestId = old_interpretation_request_rd.InterpretationRequestID
        new_interpretation_request.tieringVersion = old_interpretation_request_rd.TieringVersion
        new_interpretation_request.tieredVariants = self.migrate_tiered_variants(old_tiered_variants=old_interpretation_request_rd.TieredVariants)
        new_interpretation_request.bams = self.migrate_files(old_files=old_interpretation_request_rd.BAMs)
        new_interpretation_request.vcfs = self.migrate_files(old_files=old_interpretation_request_rd.VCFs)
        new_interpretation_request.bigWigs = self.migrate_files(old_files=old_interpretation_request_rd.bigWigs)
        new_interpretation_request.pedigreeDiagram = self.migrate_file(old_file=old_interpretation_request_rd.pedigreeDiagram)
        new_interpretation_request.annotationFile = self.migrate_file(old_file=old_interpretation_request_rd.annotationFile)
        new_interpretation_request.analysisReturnUri = old_interpretation_request_rd.analysisReturnURI
        new_interpretation_request.internalStudyId = ''

        if new_interpretation_request.validate(new_interpretation_request.toJsonDict()):
            return new_interpretation_request
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(new_interpretation_request.validate_parts())
            )

    def migrate_report_event(self, old_report_event):
        new_report_event = self.new_model.ReportEvent.fromJsonDict(old_report_event.toJsonDict())
        variant_classification_map = {
            self.old_model.VariantClassification.PATHOGENIC: self.new_model.VariantClassification.pathogenic_variant,
            self.old_model.VariantClassification.LIKELY_PATHOGENIC: self.new_model.VariantClassification.likely_pathogenic_variant,
            self.old_model.VariantClassification.VUS: self.new_model.VariantClassification.variant_of_unknown_clinical_significance,
            self.old_model.VariantClassification.LIKELY_BENIGN: self.new_model.VariantClassification.likely_benign_variant,
            self.old_model.VariantClassification.BENIGN: self.new_model.VariantClassification.benign_variant,
        }
        new_report_event.variantClassification = variant_classification_map.get(
            old_report_event.variantClassification, self.new_model.VariantClassification.not_assessed
        )

        if new_report_event.validate(new_report_event.toJsonDict()):
            return new_report_event
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(new_report_event.validate_parts())
            )

    def migrate_report_events(self, old_report_events):
        return [self.migrate_report_event(old_report_event) for old_report_event in old_report_events]

    def migrate_tiered_variant(self, old_tiered_variant):
        new_tiered_variant = self.new_model.ReportedVariant.fromJsonDict(old_tiered_variant.toJsonDict())
        new_tiered_variant.dbSnpId = old_tiered_variant.dbSNPid
        new_tiered_variant.reportEvents = self.migrate_report_events(old_report_events=old_tiered_variant.reportEvents)

        if new_tiered_variant.validate(new_tiered_variant.toJsonDict()):
            return new_tiered_variant
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(new_tiered_variant.validate_parts())
            )

    def migrate_tiered_variants(self, old_tiered_variants):
        return [self.migrate_tiered_variant(old_tiered_variant=old_tiered_variant) for old_tiered_variant in old_tiered_variants]

    def migrate_file(self, old_file):
        if old_file is None:
            return None
        if isinstance(old_file.SampleId, list):
            sampleId = old_file.SampleId
        else:
            sampleId = [old_file.SampleId]
        new_file = self.new_model.File(
                fileType=old_file.fileType,
                uriFile=old_file.URIFile,
                sampleId=sampleId,
                md5Sum=old_file.md5Sum,
            )
        if new_file.validate(new_file.toJsonDict()):
            return new_file
        else:
            raise Exception(
                'This model can not be converted: ', handle_avro_errors(new_file.validate_parts()), new_file.validate(new_file.toJsonDict(), verbose=True).messages
            )

    def migrate_files(self, old_files):
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

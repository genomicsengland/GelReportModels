from protocols import reports_3_0_0
from protocols import reports_4_0_0
from protocols.migration import BaseMigration
from protocols.migration.migration_reports_3_0_0_to_participant_1_0_0 import MigrateReports3ToParticipant1
from protocols.migration.participants import MigrationReportsToParticipants1


class MigrateReports3To4(BaseMigration):

    old_model = reports_3_0_0
    new_model = reports_4_0_0
    re_counter = 1

    def migrate_reported_somatic_variants(self, old_reported_somatic_variants):
        """
        :type old_reported_somatic_variants: reports_3_0_0.ReportedSomaticVariants
        :rtype: reports_4_0_0.ReportedSomaticVariants
        """
        new_reported_somatic_variants = self.new_model.ReportedSomaticVariants()

        old_reported_variant_cancer = old_reported_somatic_variants.reportedVariantCancer
        new_reported_somatic_variants.reportedVariantCancer = self.new_model.ReportedVariantCancer(
            clinVarIds=[''],
            additionalNumericVariantAnnotations=old_reported_variant_cancer.additionalNumericVariantAnnotations,
            additionalTextualVariantAnnotations=old_reported_variant_cancer.additionalTextualVariantAnnotations,
            vaf=old_reported_variant_cancer.VAF,
            cosmicIds=old_reported_variant_cancer.CosmicIds,
            ihp=old_reported_variant_cancer.IHP,
            alternate=old_reported_variant_cancer.alternate,
            cDnaChange=old_reported_variant_cancer.cDNAchange,
            chromosome=old_reported_variant_cancer.chromosome,
            comments=old_reported_variant_cancer.comments,
            commonAf=old_reported_variant_cancer.commonAF,
            dbSnpId=old_reported_variant_cancer.dbSNPid,
            depthAlternate=old_reported_variant_cancer.depthAlternate,
            depthReference=old_reported_variant_cancer.depthReference,
            position=old_reported_variant_cancer.position,
            proteinChange=old_reported_variant_cancer.proteinChange,
            reference=old_reported_variant_cancer.reference,
            reportEvents=old_reported_variant_cancer.reportEvents,
        )

        allele_origins_map = {
            reports_3_0_0.SomaticOrGermline.somatic: reports_4_0_0.AlleleOrigin.somatic_variant,
            reports_3_0_0.SomaticOrGermline.germline: reports_4_0_0.AlleleOrigin.germline_variant,
        }
        old_variant = old_reported_somatic_variants.somaticOrGermline
        new_reported_somatic_variants.alleleOrigins = [allele_origins_map.get(old_variant)]

        new_report_events_cancer = [
            self.migrate_report_event_cancer(event) for event in old_reported_variant_cancer.reportEvents
        ]
        new_reported_somatic_variants.reportedVariantCancer.reportEvents = new_report_events_cancer

        return self.validate_object(
            object_to_validate=new_reported_somatic_variants, object_type=self.new_model.ReportedSomaticVariants
        )

    def migrate_action(self, action):
        new_action = self.new_model.Actions().fromJsonDict(jsonDict=action.toJsonDict())
        new_action.variantActionable = action.variantActionable or False
        return self.validate_object(
            object_to_validate=new_action, object_type=self.new_model.Actions
        )

    def migrate_actions(self, actions):
        return [self.migrate_action(action=action) for action in actions]

    def migrate_report_event_cancer(self, old_report_event_cancer):

        new_report_event_cancer = self.new_model.ReportEventCancer(
            eventJustification='',
            soTerms=[],
            actions=self.migrate_actions(actions=old_report_event_cancer.actions),
            genomicFeatureCancer=old_report_event_cancer.genomicFeatureCancer,
            tier=old_report_event_cancer.tier,
            reportEventId='RE' + str(self.re_counter) if old_report_event_cancer.reportEventId in ['None', '']
            else old_report_event_cancer.reportEventId
        )

        self.re_counter += 1
        if new_report_event_cancer.genomicFeatureCancer.roleInCancer not in ['oncogene', 'TSG', 'both']:
            new_report_event_cancer.genomicFeatureCancer.roleInCancer = None

        for name, term in zip(old_report_event_cancer.soNames, old_report_event_cancer.soTerms):
            new_report_event_cancer.soTerms.append(self.new_model.SoTerm(id=term, name=name))

        return self.validate_object(
            object_to_validate=new_report_event_cancer, object_type=self.new_model.ReportEventCancer
        )

    def migrate_cancer_interpretation_request(self, old_interpretation_request):

        """

        :param old_interpretation_request:
        :type old_interpretation_request: reports_3_0_0.CancerInterpretationRequest
        """

        m = MigrateReports3ToParticipant1()
        new_cancer_interpretation_request = self.new_model.CancerInterpretationRequest(
            additionalInfo=old_interpretation_request.additionalInfo,
            analysisUri=old_interpretation_request.analysisURI,
            analysisVersion=old_interpretation_request.analysisVersion,
            annotationFile=old_interpretation_request.annotationFile,
            bams=old_interpretation_request.BAMs,
            bigWigs=old_interpretation_request.bigWigs,
            cancerParticipant=m.migrate_cancer_participant(old_interpretation_request.cancerParticipant),
            internalStudyId="1",
            interpretGenome=old_interpretation_request.interpretGenome,
            reportRequestId=old_interpretation_request.reportRequestId,
            reportVersion=old_interpretation_request.reportVersion,
            structuralTieredVariants=old_interpretation_request.structuralTieredVariants,
            tieredVariants=[
                self.migrate_reported_somatic_variants(v) for v in old_interpretation_request.TieredVariants
                ],
            tieringVersion=old_interpretation_request.TieringVersion,
            vcfs=[self.new_model.File(
                uriFile=f.URIFile,
                sampleId=[f.SampleId],
                fileType=f.fileType
            ) for f in old_interpretation_request.VCFs],
            workspace=old_interpretation_request.workspace,
        )
        # new_cancer_interpretation_request.bigWigs = []

        new_cancer_interpretation_request.versionControl = self.new_model.ReportVersionControl()

        if new_cancer_interpretation_request.validate(new_cancer_interpretation_request.toJsonDict()):
            return new_cancer_interpretation_request
        else:
            raise Exception('This model can not be converted: ',  new_cancer_interpretation_request.validate(new_cancer_interpretation_request.toJsonDict(), verbose=True).messages)

    def migrate_tiered_variant(self, old_tiered_variant):
        new_instance = self.convert_class(self.new_model.ReportedVariant, old_tiered_variant)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ReportedVariant
        )

    def migrate_tiered_variants(self, old_tiered_variants):
        return [
            self.migrate_tiered_variant(old_tiered_variant=old_tiered_variant)
            for old_tiered_variant in old_tiered_variants
        ]

    def migrate_interpretation_request_rd(self, old_instance):
        new_instance = self.convert_class(self.new_model.InterpretationRequestRD, old_instance)

        new_instance.interpretationRequestId = old_instance.InterpretationRequestID
        new_instance.interpretationRequestVersion = old_instance.InterpretationRequestVersion
        new_instance.bams = self.migrate_files(old_files=old_instance.BAMs)
        new_instance.vcfs = self.migrate_files(old_files=old_instance.VCFs)
        new_instance.bigWigs = self.migrate_files(old_files=old_instance.bigWigs)
        new_instance.tieredVariants = self.migrate_tiered_variants(old_tiered_variants=old_instance.TieredVariants)
        new_instance.tieringVersion = old_instance.TieringVersion
        new_instance.analysisReturnUri = old_instance.analysisReturnURI
        new_instance.pedigree = MigrationReportsToParticipants1().migrate_pedigree(pedigree=old_instance.pedigree)
        new_instance.internalStudyId = ''

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD
        )

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
        return self.validate_object(
            object_to_validate=new_file, object_type=self.new_model.File
        )

    def migrate_files(self, old_files):
        return None if old_files is None else [self.migrate_file(old_file=old_file) for old_file in old_files]

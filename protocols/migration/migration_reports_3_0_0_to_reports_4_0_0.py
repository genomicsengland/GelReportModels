from protocols import reports_3_0_0
from protocols import reports_4_0_0
from protocols.migration import BaseMigration
from protocols.migration.participants import MigrationReportsToParticipants1
from protocols.migration.migration_reports_3_0_0_to_participant_1_0_0 import MigrateReports3ToParticipant1


class MigrateReports3To4(BaseMigration):

    old_model = reports_3_0_0
    new_model = reports_4_0_0
    re_counter = 1

    def migrate_rd_exit_questionnaire(self, old_instance):
        """
        :type old_instance: reports_3_0_0.RareDiseaseExitQuestionnaire
        :rtype: reports_4_0_0.RareDiseaseExitQuestionnaire
        """
        new_instance = self.convert_class(self.new_model.RareDiseaseExitQuestionnaire,
                                          old_instance) # type: reports_4_0_0.RareDiseaseExitQuestionnaire
        new_instance.variantGroupLevelQuestions = [
            self.migrate_variant_group_questions(q) for q in old_instance.variantGroupLevelQuestions]
        return new_instance

    def migrate_variant_group_questions(self, old_instance):
        """
        :type old_instance: reports_3_0_0.VariantGroupLevelQuestions
        :rtype:  reports_4_0_0.VariantGroupLevelQuestions
        """
        new_instance = self.convert_class(
            self.new_model.VariantGroupLevelQuestions, old_instance)  # type: reports_4_0_0.VariantGroupLevelQuestions
        new_instance.variantGroup = old_instance.variant_group
        new_instance.variantLevelQuestions = [
            self.migrate_variant_questions(q) for q in old_instance.variantLevelQuestions]
        return new_instance

    def migrate_variant_questions(self, old_instance):
        """
        :type old_instance: reports_3_0_0.VariantLevelQuestions
        :rtype: reports_4_0_0.VariantLevelQuestions
        """
        new_instance = self.convert_class(
            self.new_model.VariantLevelQuestions, old_instance)  # type: reports_4_0_0.VariantLevelQuestions
        new_instance.variantDetails = old_instance.variant_details
        return new_instance

    def migrate_reported_somatic_variants(self, old_reported_somatic_variants):
        """
        :type old_reported_somatic_variants: reports_3_0_0.ReportedSomaticVariants
        :rtype: reports_4_0_0.ReportedSomaticVariants
        """
        new_reported_somatic_variants = self.new_model.ReportedSomaticVariants()

        old_reported_variant_cancer = old_reported_somatic_variants.reportedVariantCancer
        new_reported_somatic_variants.reportedVariantCancer = self.convert_class(
            self.new_model.ReportedVariantCancer, old_reported_variant_cancer)
        new_reported_somatic_variants.reportedVariantCancer.clinVarIds = ['']

        allele_origins_map = {
            reports_3_0_0.SomaticOrGermline.somatic: reports_4_0_0.AlleleOrigin.somatic_variant,
            reports_3_0_0.SomaticOrGermline.germline: reports_4_0_0.AlleleOrigin.germline_variant,
        }
        old_allele_origin = old_reported_somatic_variants.somaticOrGermline
        new_allele_origin = allele_origins_map.get(old_allele_origin, None)
        new_reported_somatic_variants.alleleOrigins = []
        if new_allele_origin:
            new_reported_somatic_variants.alleleOrigins.append(new_allele_origin)

        if old_reported_variant_cancer.reportEvents is not None:
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
        if actions is not None:
            return [self.migrate_action(action=action) for action in actions]
        return None

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

        if old_report_event_cancer.soNames is not None and old_report_event_cancer.soTerms is not None:
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
            annotationFile=self.migrate_file(old_interpretation_request.annotationFile),
            bams=self.migrate_files(old_interpretation_request.BAMs),
            bigWigs=self.migrate_files(old_interpretation_request.bigWigs),
            cancerParticipant=m.migrate_cancer_participant(old_interpretation_request.cancerParticipant),
            internalStudyId="1",
            interpretGenome=old_interpretation_request.interpretGenome,
            reportRequestId=old_interpretation_request.reportRequestId,
            reportVersion=old_interpretation_request.reportVersion,
            structuralTieredVariants=old_interpretation_request.structuralTieredVariants,
            tieredVariants=[
                self.migrate_reported_somatic_variants(v) for v in old_interpretation_request.TieredVariants],
            tieringVersion=old_interpretation_request.TieringVersion,
            vcfs=self.migrate_files(old_interpretation_request.VCFs),
            workspace=old_interpretation_request.workspace,
        )
        # new_cancer_interpretation_request.bigWigs = []

        new_cancer_interpretation_request.versionControl = self.new_model.ReportVersionControl()

        if new_cancer_interpretation_request.validate(new_cancer_interpretation_request.toJsonDict(), verbose=True):
            return new_cancer_interpretation_request
        else:
            raise Exception('This model can not be converted: ',  new_cancer_interpretation_request.validate(new_cancer_interpretation_request.toJsonDict(), verbose=True).messages)

    def migrate_clinical_report_rd(self, old_clinical_report_rd):
        """
        :type old_clinical_report_rd: reports_3_0_0.ClinicalReportRD
        :rtype: reports_4_0_0.ClinicalReportRD
        """
        new_clinical_report_rd = self.convert_class(self.new_model.ClinicalReportRD, old_clinical_report_rd)

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

    def migrate_reported_variant(self, old_reported_variant):
        new_tiered_variant = self.new_model.ReportedVariant.fromJsonDict(old_reported_variant.toJsonDict())
        new_tiered_variant.dbSnpId = old_reported_variant.dbSNPid
        new_tiered_variant.reportEvents = self.migrate_report_events(
            old_report_events=old_reported_variant.reportEvents
        )
        return self.validate_object(object_to_validate=new_tiered_variant, object_type=self.new_model.ReportedVariant)

    def migrate_reported_variants(self, old_reported_variants):
        if old_reported_variants is not None:
            return [
                self.migrate_reported_variant(
                    old_reported_variant=old_reported_variant
                ) for old_reported_variant in old_reported_variants
            ]
        return None

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

    def migrate_interpreted_genome_rd(self, old_instance):
        """
        :type old_interpreted_genome_rd: reports_3_0_0.InterpretedGenomeRD
        :rtype: reports_4_0_0.InterpretedGenomeRD
        """
        new_instance = self.convert_class(self.new_model.InterpretedGenomeRD, old_instance)

        new_instance.interpretationRequestId = old_instance.InterpretationRequestID
        new_instance.reportUrl = old_instance.reportURL
        new_instance.reportUri = old_instance.reportURI

        new_instance.reportedVariants = self.migrate_reported_variants(
            old_reported_variants=old_instance.reportedVariants
        )

        new_instance.reportedStructuralVariants = self.migrate_reported_structural_variants(
            old_reported_structural_variants=old_instance.reportedStructuralVariants
        )

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretedGenomeRD
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

        new_report_event.genomicFeature = self.migrate_genomic_feature(
            old_genomic_feature=old_report_event.genomicFeature)

        return self.validate_object(object_to_validate=new_report_event, object_type=self.new_model.ReportEvent)

    def migrate_genomic_feature(self, old_genomic_feature):
        new_genomic_feature = self.new_model.GenomicFeature()
        new_genomic_feature.featureType = old_genomic_feature.featureType
        new_genomic_feature.ensemblId = old_genomic_feature.ensemblId
        new_genomic_feature.hgnc = old_genomic_feature.HGNC
        new_genomic_feature.otherIds = old_genomic_feature.other_ids

        return self.validate_object(object_to_validate=new_genomic_feature, object_type=self.new_model.GenomicFeature)

    def migrate_report_events(self, old_report_events):
        if old_report_events is not None:
            return [self.migrate_report_event(old_report_event) for old_report_event in old_report_events]
        return None

    def migrate_tiered_variant(self, old_instance):
        """

        :type old_instance: reports_3_0_0.ReportedVariant
        :type assembly: reports_5_0_0.Assembly
        :type sample_id: str
        :rtype reports_4_0_0.ReportedVariant
        :return:
        """
        new_instance = self.convert_class(
            self.new_model.ReportedVariant, old_instance)  # :type: reports_5_0_0.ReportedVariant
        new_instance.dbSnpId = old_instance.dbSNPid
        if old_instance.reportEvents is not None:
            new_instance.reportEvents = [self.migrate_report_event(x) for x in old_instance.reportEvents]

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ReportedVariant
        )

    def migrate_tiered_variants(self, old_tiered_variants):
        if old_tiered_variants is not None:
            return [
                self.migrate_tiered_variant(old_instance=old_tiered_variant)
                for old_tiered_variant in old_tiered_variants
            ]
        return None

    def migrate_interpretation_request_rd(self, old_instance):
        new_instance = self.convert_class(self.new_model.InterpretationRequestRD, old_instance)

        new_instance.interpretationRequestId = old_instance.InterpretationRequestID
        new_instance.interpretationRequestVersion = old_instance.InterpretationRequestVersion
        new_instance.bams = self.migrate_files(old_files=old_instance.BAMs)
        new_instance.vcfs = self.migrate_files(old_files=old_instance.VCFs)
        new_instance.bigWigs = self.migrate_files(old_files=old_instance.bigWigs)
        new_instance.pedigreeDiagram = self.migrate_file(old_file=old_instance.pedigreeDiagram)
        new_instance.annotationFile = self.migrate_file(old_file=old_instance.annotationFile)
        new_instance.otherFiles = self.migrate_files(old_files=old_instance.otherFiles)
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
            sample_id = old_file.SampleId
        elif old_file.SampleId is None:
            sample_id = None
        else:
            sample_id = [old_file.SampleId]
        new_file = self.new_model.File(
                fileType=old_file.fileType,
                uriFile=old_file.URIFile,
                sampleId=sample_id,
                md5Sum=None,
            )
        return self.validate_object(
            object_to_validate=new_file, object_type=self.new_model.File
        )

    def migrate_files(self, old_files):
        if isinstance(old_files, list):
            return None if old_files is None else [self.migrate_file(old_file=old_file) for old_file in old_files]
        elif isinstance(old_files, dict):
            return None if old_files is None else \
                {key: self.migrate_file(old_file=old_file) for (key, old_file) in old_files.items()}

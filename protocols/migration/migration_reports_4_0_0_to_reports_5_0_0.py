from protocols import reports_4_0_0 as reports_4_0_0
from protocols import reports_5_0_0 as reports_5_0_0
from protocols import opencb_1_3_0 as opencb_1_3_0
from protocols.migration.base_migration import BaseMigration, MigrationError


class MigrateReports400To500(BaseMigration):

    old_model = reports_4_0_0
    new_model = reports_5_0_0

    def migrate_interpretation_request_rd(self, old_instance, assembly, sample_id, interpretation_service,
                                          reference_database_versions,
                                          software_versions, report_url=None, comments=None):
        """
        Migrates an InterpretationRequestRD into an InterpreteGenomeRD, several unexisting fields need to be provided
        :type old_instance: reports_4_0_0.InterpretationRequestRD
        :type assembly: reports_5_0_0.Assembly
        :type sample_id: str
        :type interpretation_service: str
        :type reference_database_versions: dict
        :type software_versions: dict
        :type report_url: str
        :type comments: list
        :rtype: reports_5_0_0.InterpretedGenomeRD
        """
        new_instance = self.convert_class(self.new_model.InterpretedGenomeRD, old_instance)

        # missing fields not existing in reports_4_0_0.InterpretationRequestRD will be received as parameters
        new_instance.interpretationService = interpretation_service
        new_instance.referenceDatabaseVersions = reference_database_versions
        new_instance.softwareVersions = software_versions
        new_instance.reportUrl = report_url
        new_instance.comments = comments

        # converts all reported variants
        new_instance.variants = self.migrate_reported_variants(old_instance.tieredVariants, assembly, sample_id)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretedGenomeRD
        )

    def migrate_interpreted_genome_rd(self, old_instance, assembly, sample_id, interpretation_request_version):
        """
        :type old_instance: reports_4_0_0.InterpretedGenomeRD
        :type assembly: reports_5_0_0.Assembly
        :type sample_id: str
        :type interpretation_request_version: str
        :rtype: reports_5_0_0.InterpretedGenomeRD
        """
        new_instance = self.convert_class(
            self.new_model.InterpretedGenomeRD, old_instance)  # type:self.new_model.InterpretedGenomeRD

        # missing fields not existing in reports_4_0_0.InterpretedGenomeRD
        new_instance.interpretationRequestVersion = interpretation_request_version

        # companyName changes to interpretationService
        new_instance.interpretationService = old_instance.companyName

        # reportUri has changed to reportUrl
        new_instance.reportUrl = old_instance.reportUri

        # converts all reported variants
        new_instance.variants = self.migrate_reported_variants(old_instance.reportedVariants, assembly, sample_id)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretedGenomeRD
        )

    def migrate_clinical_report_rd(self, old_instance, assembly, sample_id):
        """
        :type old_instance: reports_4_0_0.ClinicalReportRD
        :type sample_id: str
        :type assembly: reports_5_0_0.Assembly
        :rtype: reports_5_0_0.ClinicalReportRD
        """
        new_instance = self.convert_class(
            self.new_model.ClinicalReportRD, old_instance)  # :type self.new_model.ClinicalReportRD

        # type of interpretationRequestVersion has been changed from int to string
        try:
            new_instance.interpretationRequestVersion = int(old_instance.interpretationRequestVersion)
        except ValueError:
            raise MigrationError("Error converting 'interpretationRequestVersion' to integer from value '{}'"
                                 .format(old_instance.interpretationRequestVersion))

        # supportingEvidence has been renamed to references
        new_instance.references = old_instance.supportingEvidence

        # converts all reported variants
        new_instance.variants = self.migrate_reported_variants(old_instance.candidateVariants, assembly, sample_id)

        # converts all analysis panels
        panels = []
        for panel in old_instance.additionalAnalysisPanels:
            new_panel = self.new_model.AdditionalAnalysisPanel()  # :type reports_5_0_0.AdditionalAnalysisPanel
            new_panel.specificDisease = panel.specificDisease
            new_panel.panel = self.new_model.GenePanel(panelName=panel.panelName, panelVersion=panel.panelVersion)
            panels.append(new_panel)
        new_instance.additionalAnalysisPanels = panels

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ClinicalReportRD
        )

    def migrate_cancer_interpretation_request(self, old_instance, assembly, participant_id, sample_id,
                                              interpretation_service, reference_database_versions,
                                              software_versions, report_url=None, comments=None):
        """
        :type old_instance: reports_4_0_0.CancerInterpretationRequest
        :type assembly: reports_5_0_0.Assembly
        :type participant_id: str
        :type sample_id: str
        :type interpretation_service: str
        :type reference_database_versions: dict
        :type software_versions: dict
        :type report_url: str
        :type comments: list
        :rtype: reports_5_0_0.CancerInterpretedGenome
        """
        new_instance = self.convert_class(
            self.new_model.CancerInterpretedGenome, old_instance)  # :type: reports_5_0_0.CancerInterpretedGenome

        # reportRequest id and version are interpretationRequest id and version
        new_instance.interpretationRequestId = old_instance.reportRequestId
        new_instance.interpretationRequestVersion = old_instance.reportVersion

        # missing fields not existing in reports_4_0_0.InterpretationRequestRD will be received as parameters
        new_instance.interpretationService = interpretation_service
        new_instance.referenceDatabaseVersions = reference_database_versions
        new_instance.softwareVersions = software_versions
        new_instance.reportUrl = report_url
        new_instance.comments = comments

        # converts all reported variants
        new_instance.variants = self.migrate_reported_variants_cancer(old_instance.tieredVariants,
                                                                      assembly, participant_id, sample_id)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.CancerInterpretedGenome
        )

    def migrate_cancer_interpreted_genome(self, old_instance,
                                          assembly, participant_id, sample_id,
                                          interpretation_request_version, interpretation_service):
        """
        :type old_instance: reports_4_0_0.CancerInterpretedGenome
        :type assembly: reports_5_0_0.Assembly
        :type participant_id: str
        :type sample_id: str
        :type interpretation_request_version: int
        :type interpretation_service: str
        :rtype: reports_5_0_0.CancerInterpretedGenome
        """
        new_instance = self.new_model.CancerInterpretedGenome.fromJsonDict(
            jsonDict=old_instance.toJsonDict())  # :type: reports_5_0_0.CancerInterpretedGenome

        # reportRequestId are interpretationRequestId
        new_instance.interpretationRequestId = old_instance.reportRequestId

        # interpretation request version has to be provided
        new_instance.interpretationRequestVersion = interpretation_request_version

        # interpretation service has to be provided
        new_instance.interpretationService = interpretation_service

        # reportUri has changed to reportUrl
        new_instance.reportUrl = old_instance.reportUri

        # NOTE: field reports_4_0_0.CancerInterpretedGenome.analysisId is lost in this migration

        # converts all reported variants
        new_instance.variants = self.migrate_reported_variants_cancer(old_instance.reportedVariants,
                                                                      assembly, participant_id, sample_id)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.CancerInterpretedGenome
        )

    def migrate_cancer_clinical_report(self, old_instance, assembly, participant_id, sample_id):
        """
        :type old_instance: reports_4_0_0.ClinicalReportCancer
        :type assembly: reports_5_0_0.Assembly
        :type participant_id: str
        :type sample_id: str
        :rtype: reports_5_0_0.ClinicalReportCancer
        """
        new_instance = self.convert_class(
            self.new_model.ClinicalReportCancer, old_instance)  # :type: reports_5_0_0.ClinicalReportCancer

        # type of interpretationRequestVersion has been changed from int to string
        try:
            new_instance.interpretationRequestVersion = int(old_instance.interpretationRequestVersion)
        except ValueError:
            raise MigrationError("Error converting 'interpretationRequestVersion' to integer from value '{}'"
                                 .format(old_instance.interpretationRequestVersion))

        # converts all reported variants
        new_instance.variants = self.migrate_reported_variants_cancer(old_instance.candidateVariants,
                                                                      assembly, participant_id, sample_id)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ClinicalReportCancer
        )

    def migrate_reported_variant(self, old_instance, assembly, sample_id):
        """

        :type old_instance: reports_4_0_0.ReportedVariant
        :type assembly: reports_5_0_0.Assembly
        :type sample_id: str
        :rtype reports_5_0_0.ReportedVariant
        :return:
        """
        new_instance = self.convert_class(
            self.new_model.ReportedVariant, old_instance)  # :type: reports_5_0_0.ReportedVariant

        # builds up the variant coordinates
        new_instance.variantCoordinates = reports_5_0_0.VariantCoordinates(
            chromosome=old_instance.chromosome,
            position=old_instance.position,
            reference=old_instance.reference,
            alternate=old_instance.alternate,
            assembly=assembly
        )

        # NOTE: missing fields: dbSnpId, cosmicIds, clinVarIds, genomicChange, cdnaChanges, proteinChanges

        # converts a list of called genotypes into a list of variant calls
        variant_calls = []
        for called_genotype in old_instance.calledGenotypes:
            variant_calls.append(self.migrate_called_genotype_to_variant_call(called_genotype, sample_id))
        new_instance.variantCalls = variant_calls

        # converts a list of report events
        new_instance.reportEvents = self.migrate_report_events(old_instance.reportEvents)

        # rename field evidenceIds to references
        new_instance.references = old_instance.evidenceIds

        # TODO: fields that are not filled: variantAttributes, alleleFrequencies, alleleOrigins,
        # TODO: dbSnpId, cosmicIds, clinVarIds, genomicChange, cdnaChanges, proteinChanges

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ReportedVariant
        )

    def migrate_reported_variants(self, old_reported_variants, assembly, sample_id):
        return [self.migrate_reported_variant(old_reported_variant, assembly, sample_id)
                for old_reported_variant in old_reported_variants]

    def migrate_called_genotype_to_variant_call(self, old_instance, sample_id):
        """

        :type old_instance: reports_4_0_0.CalledGenotype
        :type sample_id: str
        :rtype reports_5_0_0.VariantCall
        :return:
        """
        new_instance = self.convert_class(
            self.new_model.VariantCall, old_instance)  # :type: reports_5_0_0.VariantCall

        # rename gelId to participantId
        new_instance.participantId = old_instance.gelId

        new_instance.sampleId = sample_id

        # rename genotype to zygosity
        new_instance.zygosity = old_instance.genotype

        # NOTE: fields that are lost: copyNumber
        # NOTE: fields that cannot be filled: vaf, alleleOrigins

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.VariantCall
        )

    def migrate_report_event(self, old_instance):
        """

        :type old_instance: reports_4_0_0.ReportEvent
        :rtype reports_5_0_0.ReportEvent
        :return:
        """
        new_instance = self.convert_class(self.new_model.ReportEvent, old_instance)

        # phenotypes has been changed to a list
        new_instance.phenotypes = [old_instance.phenotype]

        # panelName and panelVersion are now inside a dedicated object
        new_instance.genePanel = self.new_model.GenePanel(
            panelName=old_instance.panelName, panelVersion=old_instance.panelVersion)

        # genomic feature has been changed to a list
        new_instance.genomicFeatures = [self.migrate_genomic_feature(old_instance.genomicFeature)]

        # variant classification is now in a complex object
        map_variant_classification = {
            reports_4_0_0.VariantClassification.benign_variant: reports_5_0_0.ClinicalSignificance.benign,
            reports_4_0_0.VariantClassification.likely_benign_variant: reports_5_0_0.ClinicalSignificance.likely_benign,
            reports_4_0_0.VariantClassification.variant_of_unknown_clinical_significance:
                reports_5_0_0.ClinicalSignificance.VUS,
            reports_4_0_0.VariantClassification.likely_pathogenic_variant:
                reports_5_0_0.ClinicalSignificance.likely_pathogenic,
            reports_4_0_0.VariantClassification.pathogenic_variant: reports_5_0_0.ClinicalSignificance.pathogenic
        }
        new_instance.variantClassification = opencb_1_3_0.VariantClassification(
            clinicalSignificance=map_variant_classification[old_instance.variantClassification]
        )

        # NOTE: consequence types cannot be filled, but it is not nullable so we are creating an empty list
        new_instance.consequenceTypes = []

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ReportEvent
        )

    def migrate_report_events(self, old_report_events):
        return [self.migrate_report_event(old_report_event) for old_report_event in old_report_events]

    def migrate_genomic_feature(self, old_instance):
        """

                :type old_instance: reports_4_0_0.GenomicFeature
                :rtype reports_5_0_0.GenomicFeature
                :return:
                """
        new_instance = self.convert_class(self.new_model.GenomicFeature, old_instance)

        # rename field HGNC to gene symbol
        new_instance.geneSymbol = old_instance.hgnc

        # enum feature type has been renamed
        map_feature_type = {
            reports_4_0_0.FeatureTypes.Transcript: reports_5_0_0.FeatureTypes.transcript,
            reports_4_0_0.FeatureTypes.RegulatoryRegion: reports_5_0_0.FeatureTypes.regulatory_region,
            reports_4_0_0.FeatureTypes.Gene: reports_5_0_0.FeatureTypes.gene
        }
        new_instance.featureType = map_feature_type[old_instance.featureType]

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.GenomicFeature
        )

    def migrate_reported_variant_cancer(self, old_instance, assembly, participant_id, sample_id):
        """

        :type old_instance: reports_4_0_0.ReportedSomaticVariants
        :type assembly: reports_5_0_0.Assembly
        :type participant_id: str
        :type sample_id: str
        :rtype reports_5_0_0.ReportedVariantCancer
        :return:
        """
        new_instance = self.convert_class(
            self.new_model.ReportedVariantCancer,
            old_instance.reportedVariantCancer)  # :type: reports_5_0_0.ReportedVariant

        # builds up the variant coordinates
        new_instance.variantCoordinates = reports_5_0_0.VariantCoordinates(
            chromosome=old_instance.reportedVariantCancer.chromosome,
            position=old_instance.reportedVariantCancer.position,
            reference=old_instance.reportedVariantCancer.reference,
            alternate=old_instance.reportedVariantCancer.alternate,
            assembly=assembly
        )

        # field cDnaChange renamed to cdnaChange
        new_instance.cdnaChanges = old_instance.reportedVariantCancer.cDnaChange

        # field proteinChange changed to a list
        new_instance.proteinChanges = [old_instance.reportedVariantCancer.proteinChange]

        # NOTE: missing fields: genomicChanges

        # builds up the VariantCall object
        new_instance.variantCalls = [reports_5_0_0.VariantCall(
            depthReference=old_instance.reportedVariantCancer.depthReference,
            depthAlternate=old_instance.reportedVariantCancer.depthAlternate,
            vaf=old_instance.reportedVariantCancer.vaf,
            zygosity=reports_5_0_0.Zygosity.na,
            alleleOrigins=old_instance.alleleOrigins,
            participantId=participant_id,
            sampleId=sample_id
        )]

        # builds up an AlleleFrequency object
        new_instance.alleleFrequencies = [reports_5_0_0.AlleleFrequency(
            study='genomics_england',
            population='ALL',
            alternateFrequency=float(old_instance.reportedVariantCancer.commonAf)
            if old_instance.reportedVariantCancer.commonAf is not None else None
        )]

        # builds up the VariantAttributes
        new_instance.variantAttributes = reports_5_0_0.VariantAttributes(
            ihp=old_instance.reportedVariantCancer.ihp
        )

        # list of allele origins is flattened and received as a parameter
        new_instance.alleleOrigins = old_instance.alleleOrigins

        # migrates cancer report events
        new_instance.reportEvents = self.migrate_report_events_cancer(old_instance.reportedVariantCancer.reportEvents)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ReportedVariantCancer
        )

    def migrate_reported_variants_cancer(self, old_reported_variants, assembly, participant_id, sample_id):
        return [self.migrate_reported_variant_cancer(old_reported_variant, assembly, participant_id, sample_id)
                for old_reported_variant in old_reported_variants]

    def migrate_report_event_cancer(self, old_instance):
        """

        :type old_instance: reports_4_0_0.ReportEventCancer
        :rtype reports_5_0_0.ReportEventCancer
        :return:
        """
        new_instance = self.convert_class(self.new_model.ReportEventCancer, old_instance)

        # map one genomic feature cancer into a list of common genomic features
        new_instance.genomicFeatures = [self.migrate_genomic_feature_cancer(old_instance.genomicFeatureCancer)]

        # transforms a list of SO terms into a list of consequence types
        new_instance.consequenceTypes = [reports_5_0_0.ConsequenceTypes(id=so_term.id, name=so_term.name)
                                         for so_term in old_instance.soTerms]

        # migrates actions
        new_instance.actions = self.migrate_actions(old_instance.actions)

        # populates the role in cancer with the field inside the genomic feature
        map_role_in_cancer = {
            reports_4_0_0.RoleInCancer.both: reports_5_0_0.RoleInCancer.both,
            reports_4_0_0.RoleInCancer.oncogene: reports_5_0_0.RoleInCancer.oncogene,
            reports_4_0_0.RoleInCancer.TSG: reports_5_0_0.RoleInCancer.tumor_suppressor_gene
        }
        new_instance.roleInCancer = [map_role_in_cancer[old_instance.genomicFeatureCancer.roleInCancer]]

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ReportEventCancer
        )

    def migrate_report_events_cancer(self, old_report_events):
        return [self.migrate_report_event_cancer(old_report_event) for old_report_event in old_report_events]

    def migrate_genomic_feature_cancer(self, old_instance):
        """

        :type old_instance: reports_4_0_0.GenomicFeatureCancer
        :rtype reports_5_0_0.GenomicFeature
        :return:
        """
        new_instance = self.convert_class(self.new_model.GenomicFeature, old_instance)

        # maps the feature type
        map_feature_type = {
            reports_4_0_0.FeatureTypes.Transcript: reports_5_0_0.FeatureTypes.transcript,
            reports_4_0_0.FeatureTypes.RegulatoryRegion: reports_5_0_0.FeatureTypes.regulatory_region,
            reports_4_0_0.FeatureTypes.Gene: reports_5_0_0.FeatureTypes.gene
        }
        new_instance.featureType = map_feature_type[old_instance.featureType]

        # rename gene name to gene symbol
        new_instance.geneSymbol = old_instance.geneName

        # NOTE: fields refSeqTranscriptId and refSeqProteinId are lost

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.GenomicFeature
        )

    def migrate_action(self, old_instance):
        """

        :type old_instance: reports_4_0_0.Actions
        :rtype reports_5_0_0.Action
        :return:
        """
        new_instance = self.convert_class(self.new_model.Action, old_instance)

        # maps the action type
        action_type = old_instance.actionType.lower()
        if action_type == reports_5_0_0.ActionType.therapy:
            new_instance.actionType = reports_5_0_0.ActionType.therapy
        elif action_type == reports_5_0_0.ActionType.therapeutic:
            new_instance.actionType = reports_5_0_0.ActionType.therapeutic
        elif action_type == reports_5_0_0.ActionType.prognosis:
            new_instance.actionType = reports_5_0_0.ActionType.prognosis
        elif action_type == reports_5_0_0.ActionType.diagnosis:
            new_instance.actionType = reports_5_0_0.ActionType.diagnosis
        elif action_type is not None and action_type != "":
            raise MigrationError("Action type does not match any known value '{}'".format(action_type))

        # rename evidence to references
        new_instance.references = old_instance.evidence

        # maps the action status
        status = old_instance.status.lower().replace('-', '_')
        if status == reports_5_0_0.ActionStatus.clinical:
            new_instance.status = reports_5_0_0.ActionStatus.clinical
        elif status == reports_5_0_0.ActionStatus.pre_clinical:
            new_instance.status = reports_5_0_0.ActionStatus.pre_clinical
        elif status is not None and status != "":
            raise MigrationError("Action status does not match any known value '{}'".format(status))

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.Action
        )

    def migrate_actions(self, old_instances):
        return [self.migrate_action(old_instance) for old_instance in old_instances]

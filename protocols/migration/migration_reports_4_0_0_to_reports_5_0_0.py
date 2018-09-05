import logging

from protocols import reports_4_0_0 as reports_4_0_0
from protocols import reports_5_0_0 as reports_5_0_0
from protocols import opencb_1_3_0 as opencb_1_3_0
from protocols.migration.base_migration import BaseMigration, MigrationError
import itertools


class MigrateReports400To500(BaseMigration):

    old_model = reports_4_0_0
    new_model = reports_5_0_0

    def migrate_interpretation_request_rd(self, old_instance, assembly):
        """
        Migrates an InterpretationRequestRD into an InterpretedGenomeRD, several unexisting fields need to be provided
        :type old_instance: reports_4_0_0.InterpretationRequestRD
        :rtype: reports_5_0_0.InterpretationRequestRD
        """
        new_instance = self.convert_class(self.new_model.InterpretationRequestRD, old_instance)
        new_instance.genomeAssembly = assembly
        new_instance.pedigree.members = self.migrate_pedigree_members(old_members=old_instance.pedigree.members)
        new_instance.otherFiles = self.migrate_other_files(other_files=old_instance.otherFiles)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD
        )

    def migrate_interpretation_request_rd_to_interpreted_genome_rd(
            self, old_instance, assembly, interpretation_service,
            reference_database_versions, software_versions, report_url=None, comments=None):
        """
        Migrates an InterpretationRequestRD into an InterpretedGenomeRD, several unexisting fields need to be provided
        :type old_instance: reports_4_0_0.InterpretationRequestRD
        :type assembly: reports_5_0_0.Assembly
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
        new_instance.referenceDatabasesVersions = reference_database_versions
        if software_versions is None:
            software_versions = {}
        software_versions['tiering'] = old_instance.tieringVersion
        new_instance.softwareVersions = software_versions
        new_instance.reportUrl = report_url
        new_instance.comments = comments

        # converts all reported variants
        new_instance.variants = self.migrate_reported_variants(old_instance.tieredVariants, assembly)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretedGenomeRD
        )

    def migrate_interpreted_genome_rd(self, old_instance, assembly, interpretation_request_version):
        """
        :type old_instance: reports_4_0_0.InterpretedGenomeRD
        :type assembly: reports_5_0_0.Assembly
        :type interpretation_request_version: int
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
        new_instance.variants = self.migrate_reported_variants(old_instance.reportedVariants, assembly)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretedGenomeRD
        )

    def migrate_clinical_report_rd(self, old_instance, assembly):
        """
        :type old_instance: reports_4_0_0.ClinicalReportRD
        :type assembly: reports_5_0_0.Assembly
        :rtype: reports_5_0_0.ClinicalReportRD
        """
        new_instance = self.convert_class(
            self.new_model.ClinicalReportRD, old_instance)  # :type self.new_model.ClinicalReportRD

        # type of interpretationRequestVersion has been changed from int to string
        try:
            new_instance.interpretationRequestVersion = self.convert_string_to_integer(
                old_instance.interpretationRequestVersion)
        except MigrationError as ex:
            logging.error("Error converting 'interpretationRequestVersion' to integer from value '{}'".format(
                old_instance.interpretationRequestVersion))
            raise ex

        # supportingEvidence has been renamed to references
        new_instance.references = old_instance.supportingEvidence

        # converts all reported variants
        new_instance.variants = self.migrate_reported_variants(old_instance.candidateVariants, assembly)

        # converts all analysis panels
        if old_instance.additionalAnalysisPanels is not None:
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

    def migrate_cancer_interpretation_request(self, old_instance, assembly):
        """
        :type old_instance: reports_4_0_0.CancerInterpretationRequest
        :rtype: reports_5_0_0.CancerInterpretationRequest
        """
        new_instance = self.convert_class(
            self.new_model.CancerInterpretationRequest, old_instance
        )  # :type: reports_5_0_0.CancerInterpretationRequest

        new_instance.interpretationRequestId = old_instance.reportRequestId
        new_instance.interpretationRequestVersion = old_instance.reportVersion
        new_instance.genomeAssembly = assembly
        new_instance.cancerParticipant = self.migrate_cancer_participant(old_participant=old_instance.cancerParticipant)

        new_instance.otherFiles = old_instance.otherFiles

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.CancerInterpretationRequest
        )

    def migrate_cancer_interpretation_request_to_cancer_interpreted_genome(
            self, old_instance, assembly, interpretation_service,
            reference_database_versions, software_versions, report_url=None, comments=None):
        """
        NOTE: we migrate from a model where only one sample and one participant is supported, thus we do not need
        a list of samples or participants
        :type old_instance: reports_4_0_0.CancerInterpretationRequest
        :type assembly: reports_5_0_0.Assembly
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
        new_instance.referenceDatabasesVersions = reference_database_versions
        new_instance.softwareVersions = software_versions
        new_instance.reportUrl = report_url
        new_instance.comments = comments

        # converts all reported variants
        participant_id = old_instance.cancerParticipant.individualId
        tumor_samples = old_instance.cancerParticipant.tumourSamples
        if not tumor_samples:
            raise MigrationError("There is no tumour sample to perform the migration")
        elif len(tumor_samples) > 1:
            raise MigrationError("There are several tumour samples, cannot decide which to use '{}'"
                                 .format(str(tumor_samples)))
        sample_id = tumor_samples[0].sampleId
        new_instance.variants = self.migrate_reported_variants_cancer(
            old_instance.tieredVariants, assembly, participant_id, sample_id)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.CancerInterpretedGenome
        )

    def migrate_cancer_interpreted_genome(self, old_instance,
                                          assembly, participant_id, sample_id,
                                          interpretation_request_version, interpretation_service):
        """
        NOTE: we migrate from a model where only one sample and one participant is supported, thus we do not need
        a list of samples or participants
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
        NOTE: we migrate from a model where only one sample and one participant is supported, thus we do not need
        a list of samples or participants
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
            new_instance.interpretationRequestVersion = self.convert_string_to_integer(
                old_instance.interpretationRequestVersion)
        except MigrationError as ex:
            logging.error("Error converting 'interpretationRequestVersion' to integer from value '{}'".format(
                old_instance.interpretationRequestVersion))
            raise ex

        # converts all reported variants
        new_instance.variants = self.migrate_reported_variants_cancer(old_instance.candidateVariants,
                                                                      assembly, participant_id, sample_id)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ClinicalReportCancer
        )

    def migrate_reported_variant(self, old_instance, assembly, migrate_frequencies=False):
        """
        NOTE: some fields cannot be filled: alleleFrequencies, genomicChanges, proteinChanges, cdnaChanges,
        dbSnpId, cosmicIds, clinVarIds, variantAttributes, alleleFrequencies

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
            assembly=self.migrate_assembly(assembly)
        )

        # NOTE: missing fields: dbSnpId, cosmicIds, clinVarIds, genomicChange, cdnaChanges, proteinChanges

        # converts a list of called genotypes into a list of variant calls
        variant_calls = []
        if old_instance.calledGenotypes is not None:
            for called_genotype in old_instance.calledGenotypes:
                variant_calls.append(self.migrate_called_genotype_to_variant_call(called_genotype))
        new_instance.variantCalls = variant_calls

        # converts a list of report events
        new_instance.reportEvents = self.migrate_report_events(old_instance.reportEvents)

        # rename field evidenceIds to references
        new_instance.references = old_instance.evidenceIds

        # hardcodes allele origin to germline as this is a variant from rare disease program
        new_instance.alleleOrigins = [reports_5_0_0.AlleleOrigin.germline_variant]

        if migrate_frequencies:
            new_instance.alleleFrequencies = self.migrate_allele_frequencies(
                old_instance.additionalNumericVariantAnnotations)

        # TODO: fields that are not filled: variantAttributes, alleleFrequencies,
        # TODO: dbSnpId, cosmicIds, clinVarIds, genomicChange, cdnaChanges, proteinChanges

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ReportedVariant
        )

    def migrate_reported_variants(self, old_reported_variants, assembly):
        new_variants = None
        if old_reported_variants is not None:
            new_variants = [self.migrate_reported_variant(old_reported_variant, assembly)
                            for old_reported_variant in old_reported_variants]
        return new_variants

    def migrate_assembly(self, assembly):
        """
        :type assembly: str
        :rtype: str
        :return:
        """
        new_assembly = None
        if assembly is not None:
            if assembly.lower().startswith(reports_5_0_0.Assembly.GRCh37.lower()) \
                    or assembly.lower().startswith('hg19'):
                new_assembly = reports_5_0_0.Assembly.GRCh37
            elif assembly.lower().startswith(reports_5_0_0.Assembly.GRCh38.lower()):
                new_assembly = reports_5_0_0.Assembly.GRCh38
            else:
                raise MigrationError("Assembly does not match any known value '{}'".format(assembly))
        return new_assembly

    def migrate_called_genotype_to_variant_call(self, old_instance):
        """
        NOTE: fields that cannot be filled "vaf"
        :type old_instance: reports_4_0_0.CalledGenotype
        :rtype reports_5_0_0.VariantCall
        :return:
        """
        new_instance = self.convert_class(
            self.new_model.VariantCall, old_instance)  # :type: reports_5_0_0.VariantCall

        # rename gelId to participantId
        new_instance.participantId = old_instance.gelId

        # rename genotype to zygosity
        new_instance.zygosity = old_instance.genotype

        # sets allele origin to germline, we fail to set maternal/paternal origin or de novo status
        new_instance.alleleOrigins = [reports_5_0_0.AlleleOrigin.germline_variant]

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
        if old_instance.panelName is not None:
            new_instance.genePanel = self.new_model.GenePanel(
                panelName=old_instance.panelName)
            if old_instance.panelVersion is not None:
                new_instance.genePanel.panelVersion = old_instance.panelVersion

        # genomic feature has been changed to a list
        new_instance.genomicEntities = [self.migrate_genomic_feature(old_instance.genomicFeature)]

        # variant classification is now in a complex object
        if old_instance.variantClassification is not None:
            old_variant_classification = reports_4_0_0.VariantClassification
            new_clinical_significance = reports_5_0_0.ClinicalSignificance
            map_variant_classification = {
                old_variant_classification.benign_variant: new_clinical_significance.benign,
                old_variant_classification.likely_benign_variant: new_clinical_significance.likely_benign,
                old_variant_classification.variant_of_unknown_clinical_significance: new_clinical_significance.VUS,
                old_variant_classification.likely_pathogenic_variant: new_clinical_significance.likely_pathogenic,
                old_variant_classification.pathogenic_variant: new_clinical_significance.pathogenic,
                old_variant_classification.not_assessed: None
            }
            clinical_significance = map_variant_classification[old_instance.variantClassification]
            if clinical_significance is not None:
                new_instance.variantClassification = opencb_1_3_0.VariantClassification(
                    clinicalSignificance=map_variant_classification[old_instance.variantClassification]
                )

        # NOTE: variant consequences cannot be filled, but it is not nullable so we are creating an empty list
        new_instance.variantConsequences = []

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ReportEvent
        )

    def migrate_report_events(self, old_report_events):
        if old_report_events is not None:
            return [self.migrate_report_event(old_report_event) for old_report_event in old_report_events]
        return None

    def migrate_genomic_feature(self, old_instance):
        """
        # NOTE: some fields cannot be filled: otherIds
        :type old_instance: reports_4_0_0.GenomicFeature
        :rtype reports_5_0_0.GenomicEntity
        :return:
        """
        new_instance = self.convert_class(self.new_model.GenomicEntity, old_instance)

        # rename field HGNC to gene symbol
        new_instance.geneSymbol = old_instance.hgnc

        # enum feature type has been renamed
        map_feature_type = {
            reports_4_0_0.FeatureTypes.Transcript: reports_5_0_0.GenomicEntityType.transcript,
            reports_4_0_0.FeatureTypes.RegulatoryRegion: reports_5_0_0.GenomicEntityType.regulatory_region,
            reports_4_0_0.FeatureTypes.Gene: reports_5_0_0.GenomicEntityType.gene
        }
        new_instance.type = map_feature_type[old_instance.featureType]

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.GenomicEntity
        )

    def migrate_reported_variant_cancer(self, old_instance, assembly, participant_id, sample_id):
        """
        NOTE: fields that cannot be filled are "genomicChanges", "references"
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
            assembly=self.migrate_assembly(assembly)
        )

        # field cDnaChange renamed to cdnaChange
        if old_instance.reportedVariantCancer.cDnaChange:
            new_instance.cdnaChanges = [old_instance.reportedVariantCancer.cDnaChange]

        # field proteinChange changed to a list
        if old_instance.reportedVariantCancer.proteinChange:
            new_instance.proteinChanges = [old_instance.reportedVariantCancer.proteinChange]

        # NOTE: missing fields: genomicChanges

        # builds up the VariantCall object
        # NOTE: fields that cannot be filled "phaseSet"
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
        if old_instance.reportedVariantCancer.commonAf is not None:
            new_instance.alleleFrequencies = [reports_5_0_0.AlleleFrequency(
                study='genomics_england',
                population='ALL',
                alternateFrequency=self.convert_string_to_float(old_instance.reportedVariantCancer.commonAf)
            )]

        # builds up the VariantAttributes
        # NOTE: some fields cannot be filled: "fdp50", "recurrentlyReported", "others"
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
        new_variants = None
        if old_reported_variants is not None:
            new_variants = [self.migrate_reported_variant_cancer(
                old_reported_variant, assembly, participant_id, sample_id)
                for old_reported_variant in old_reported_variants]
        return new_variants

    def migrate_report_event_cancer(self, old_instance):
        """
        NOTE: fields that cannot be filled are "groupOfVariants", "score", "vendorSpecificScores", "variantClassification"
        :type old_instance: reports_4_0_0.ReportEventCancer
        :rtype reports_5_0_0.ReportEventCancer
        :return:
        """
        new_instance = self.convert_class(self.new_model.ReportEventCancer, old_instance)

        # map one genomic feature cancer into a list of common genomic features
        new_instance.genomicEntities = [self.migrate_genomic_feature_cancer(old_instance.genomicFeatureCancer)]

        # transforms a list of SO terms into a list of variant consequences
        if old_instance.soTerms is not None:
            new_instance.variantConsequences = [reports_5_0_0.VariantConsequence(id=so_term.id, name=so_term.name)
                                                for so_term in old_instance.soTerms]

        # migrates actions
        new_instance.actions = self.migrate_actions(old_instance.actions)

        # populates the role in cancer with the field inside the genomic feature
        map_role_in_cancer = {
            None: None,
            reports_4_0_0.RoleInCancer.both: [reports_5_0_0.RoleInCancer.both],
            reports_4_0_0.RoleInCancer.oncogene: [reports_5_0_0.RoleInCancer.oncogene],
            reports_4_0_0.RoleInCancer.TSG: [reports_5_0_0.RoleInCancer.tumor_suppressor_gene]
        }
        new_instance.roleInCancer = map_role_in_cancer[old_instance.genomicFeatureCancer.roleInCancer]

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ReportEventCancer
        )

    def migrate_report_events_cancer(self, old_report_events):
        if old_report_events is not None:
            return [self.migrate_report_event_cancer(old_report_event) for old_report_event in old_report_events]
        return None

    def migrate_genomic_feature_cancer(self, old_instance):
        """
        NOTE: fields that cannot be filled are "otherIds"protocols/opencb_1_3_0.py
        :type old_instance: reports_4_0_0.GenomicFeatureCancer
        :rtype reports_5_0_0.GenomicEntity
        :return:
        """
        new_instance = self.convert_class(self.new_model.GenomicEntity, old_instance)

        # maps the feature type
        map_feature_type = {
            reports_4_0_0.FeatureTypes.Transcript: reports_5_0_0.GenomicEntityType.transcript,
            reports_4_0_0.FeatureTypes.RegulatoryRegion: reports_5_0_0.GenomicEntityType.regulatory_region,
            reports_4_0_0.FeatureTypes.Gene: reports_5_0_0.GenomicEntityType.gene
        }
        new_instance.type = map_feature_type[old_instance.featureType]

        # rename gene name to gene symbol
        new_instance.geneSymbol = old_instance.geneName

        # NOTE: fields refSeqTranscriptId and refSeqProteinId are lost

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.GenomicEntity
        )

    def migrate_action(self, old_instance):
        """
        NOTE: fields that cannot be filled are "actionType"
        :type old_instance: reports_4_0_0.Actions
        :rtype reports_5_0_0.Action
        :return:
        """
        new_instance = self.convert_class(self.new_model.Action, old_instance)

        new_instance.evidenceType = old_instance.actionType
        new_instance.actionType = None

        # rename evidence to references
        new_instance.references = old_instance.evidence

        # maps the action status
        if old_instance.status is not None:
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
        new_instances = None
        if old_instances is not None:
            new_instances = [self.migrate_action(old_instance) for old_instance in old_instances]
        return new_instances

    def migrate_tumour_sample(self, old_sample, ldp_code):
        ts = self.new_model.TumourSample
        tt = self.new_model.TumourType
        new_sample = self.convert_class(ts, old_sample)  # :type: reports_5_0_0.TumourSample

        tumour_type_enum = [
            tt.PRIMARY, tt.METASTATIC_RECURRENCE, tt.RECURRENCE_OF_PRIMARY_TUMOUR, tt.METASTASES
        ]
        new_sample.tumourType = old_sample.tumourType if old_sample.tumourType in tumour_type_enum else None
        new_sample.tumourId = self.convert_int_to_str(value=old_sample.tumourId)
        if ldp_code is None:
            raise MigrationError("Cannot migrate '{}' to '{}' having an empty value of 'ldp_code'".format(
                type(old_sample), type(new_sample))
            )
        new_sample.LDPCode = ldp_code

        return self.validate_object(object_to_validate=new_sample, object_type=ts)

    def migrate_tumour_samples(self, old_samples, ldp_code):
        if old_samples is not None:
            return [
                self.migrate_tumour_sample(old_sample=old_sample, ldp_code=ldp_code) for old_sample in old_samples
                if old_samples is not None
            ]
        return None

    @staticmethod
    def convert_int_to_str(value):
        try:
            return str(value)
        except ValueError:
            return None

    def migrate_germline_sample(self, old_sample, ldp_code):
        gs = self.new_model.GermlineSample
        new_sample = self.convert_class(gs, old_sample)  # :type: reports_5_0_0.GermlineSample
        new_sample.LDPCode = ldp_code
        return self.validate_object(object_to_validate=new_sample, object_type=gs)

    def migrate_germline_samples(self, old_samples, ldp_code):
        if old_samples is not None:
            return [
                self.migrate_germline_sample(old_sample=old_sample, ldp_code=ldp_code) for old_sample in old_samples
                if old_samples is not None
            ]
        return None

    def migrate_cancer_participant(self, old_participant):
        new_participant = self.convert_class(
            self.new_model.CancerParticipant, old_participant
        )  # :type: reports_5_0_0.CancerParticipant

        new_participant.tumourSamples = self.migrate_tumour_samples(
            old_samples=old_participant.tumourSamples, ldp_code=old_participant.LDPCode
        )
        new_participant.germlineSamples = self.migrate_germline_samples(
            old_samples=old_participant.germlineSamples, ldp_code=old_participant.LDPCode
        )
        # NOTE: we create all combinations of germline and tumour as a conservative approach
        if new_participant.germlineSamples is not None and new_participant.tumourSamples is not None:
            new_participant.matchedSamples = \
                [self.new_model.MatchedSamples(germlineSampleId=x.sampleId, tumourSampleId=y.sampleId)
                 for (x, y) in list(itertools.product(new_participant.germlineSamples, new_participant.tumourSamples))]

        new_participant.primaryDiagnosisDisease = \
            [old_participant.primaryDiagnosisDisease] if old_participant.primaryDiagnosisDisease else None
        new_participant.primaryDiagnosisSubDisease = \
            [old_participant.primaryDiagnosisSubDisease] if old_participant.primaryDiagnosisSubDisease else None
        new_participant.assignedICD10 = \
            [old_participant.assignedICD10] if old_participant.assignedICD10 else None

        return self.validate_object(
            object_to_validate=new_participant, object_type=self.new_model.CancerParticipant
        )

    def migrate_disorder(self, old_disorder):
        new_object_type = self.new_model.Disorder
        new_disorder = self.convert_class(target_klass=new_object_type, instance=old_disorder)
        new_disorder.ageOfOnset = self.convert_string_to_float(old_disorder.ageOfOnset, fail=False)
        return self.validate_object(object_to_validate=new_disorder, object_type=new_object_type)

    def migrate_disorder_list(self, old_disorder_list):
        new_disorder_list = None
        if old_disorder_list is not None:
            new_disorder_list = [self.migrate_disorder(old_disorder=old_disorder) for old_disorder in old_disorder_list]
        return new_disorder_list

    def migrate_hpo_term_age_of_onset(self, old_age_of_onset):
        new_age_of_onset = None
        age_of_onset_enum = [
            self.new_model.AgeOfOnset.EMBRYONAL_ONSET,
            self.new_model.AgeOfOnset.FETAL_ONSET,
            self.new_model.AgeOfOnset.NEONATAL_ONSET,
            self.new_model.AgeOfOnset.INFANTILE_ONSET,
            self.new_model.AgeOfOnset.CHILDHOOD_ONSET,
            self.new_model.AgeOfOnset.JUVENILE_ONSET,
            self.new_model.AgeOfOnset.YOUNG_ADULT_ONSET,
            self.new_model.AgeOfOnset.LATE_ONSET,
            self.new_model.AgeOfOnset.MIDDLE_AGE_ONSET,
        ]
        if isinstance(old_age_of_onset, str):
            if old_age_of_onset.upper() in age_of_onset_enum:
                new_age_of_onset = old_age_of_onset.upper()
        return new_age_of_onset

    def migrate_hpo_term(self, old_hpo_term):
        new_object_type = self.new_model.HpoTerm
        new_hpo_term = self.convert_class(target_klass=new_object_type, instance=old_hpo_term)
        new_hpo_term.ageOfOnset = self.migrate_hpo_term_age_of_onset(old_age_of_onset=old_hpo_term.ageOfOnset)
        return self.validate_object(object_to_validate=new_hpo_term, object_type=new_object_type)

    def migrate_hpo_term_list(self, old_hpo_term_list):
        new_hpo_term_list = None
        if old_hpo_term_list is not None:
            new_hpo_term_list = [self.migrate_hpo_term(old_hpo_term=old_hpo) for old_hpo in old_hpo_term_list]
        return new_hpo_term_list

    def migrate_chiSquare1KGenomesPhase3Pop(self, old_chiSquare1KGenomesPhase3Pop):
        new_object_type = self.new_model.ChiSquare1KGenomesPhase3Pop
        new_cs1kgp3p = self.convert_class(target_klass=new_object_type, instance=old_chiSquare1KGenomesPhase3Pop)
        new_cs1kgp3p.kgSuperPopCategory = old_chiSquare1KGenomesPhase3Pop.kGSuperPopCategory
        return self.validate_object(object_to_validate=new_cs1kgp3p, object_type=new_object_type)

    def migrate_chiSquare1KGenomesPhase3Pop_list(self, old_chiSquare1KGenomesPhase3Pop_list):
        if old_chiSquare1KGenomesPhase3Pop_list is not None:
            return [
                self.migrate_chiSquare1KGenomesPhase3Pop(old_chiSquare1KGenomesPhase3Pop=old_chiSquare1KGenomesPhase3Pop)
                for old_chiSquare1KGenomesPhase3Pop in old_chiSquare1KGenomesPhase3Pop_list
            ]
        return None

    def migrate_ancestries(self, old_ancestries):
        new_object_type = self.new_model.Ancestries
        new_ancestries = self.convert_class(target_klass=new_object_type, instance=old_ancestries)
        new_ancestries.chiSquare1KGenomesPhase3Pop = self.migrate_chiSquare1KGenomesPhase3Pop_list(old_chiSquare1KGenomesPhase3Pop_list=old_ancestries.chiSquare1KGenomesPhase3Pop)
        return self.validate_object(object_to_validate=new_ancestries, object_type=new_object_type)

    def migrate_pedigree_member(self, old_member):
        new_object_type = self.new_model.PedigreeMember
        new_member = self.convert_class(target_klass=new_object_type, instance=old_member)
        new_member.disorderList = self.migrate_disorder_list(old_disorder_list=old_member.disorderList)
        new_member.hpoTermList = self.migrate_hpo_term_list(old_hpo_term_list=old_member.hpoTermList)
        if old_member.ancestries is not None:
            new_member.ancestries = self.migrate_ancestries(old_ancestries=old_member.ancestries)
        else:
            new_member.ancestries = None
        return self.validate_object(object_to_validate=new_member, object_type=new_object_type)

    def migrate_pedigree_members(self, old_members):
        if old_members is not None:
            return [self.migrate_pedigree_member(old_member) for old_member in old_members if old_members is not None]
        return None

    def migrate_other_files(self, other_files):
        if isinstance(other_files, dict):
            return {key: self.convert_class(target_klass=self.new_model.File, instance=other_file) for key, other_file in other_files.items()}

    def migrate_allele_frequencies(self, additionalNumericVariantAnnotations):
        """
        NOTE: This is assuming all values in `additionalNumericVariantAnnotations` are frequencies

        :param additionalNumericVariantAnnotations:
        :return:
        """
        frequencies = []
        for pop in additionalNumericVariantAnnotations:
            frequencies.append(reports_5_0_0.AlleleFrequency(
                alternateFrequency=additionalNumericVariantAnnotations[pop],
                population=pop.split('_')[-1],
                study='_'.join(pop.split('_')[:-1])
            ))
        return frequencies

import logging
import math

from protocols import reports_4_0_0 as reports_4_0_0
from protocols import reports_5_0_0 as reports_5_0_0
from protocols import opencb_1_3_0 as opencb_1_3_0
from protocols.migration import MigrationParticipants103To110, MigrationParticipants100To103
from protocols.migration.base_migration import MigrationError, BaseMigrateReports400And500


class MigrateReports400To500(BaseMigrateReports400And500):

    old_model = reports_4_0_0
    new_model = reports_5_0_0
    participant_migrator = MigrationParticipants100To103()

    def migrate_interpretation_request_rd(self, old_instance, assembly):
        """
        Migrates an InterpretationRequestRD into an InterpretedGenomeRD, several unexisting fields need to be provided
        :type old_instance: reports_4_0_0.InterpretationRequestRD
        :rtype: reports_5_0_0.InterpretationRequestRD
        """
        if assembly is None:
            raise MigrationError("Parameter <assembly> is required if version is older than 5.0.0")
        new_instance = self.convert_class(self.new_model.InterpretationRequestRD, old_instance)  # type: reports_5_0_0.InterpretationRequestRD
        new_instance.genomeAssembly = assembly
        new_instance.pedigree = self._migrate_pedigree(old_instance.pedigree)
        # NOTE: store fields in additional fields that are lost otherwise
        if not new_instance.additionalInfo:
            new_instance.additionalInfo = {}
        if old_instance.analysisVersion:
            new_instance.additionalInfo['analysisVersion'] = old_instance.analysisVersion
        if old_instance.analysisReturnUri:
            new_instance.additionalInfo['analysisReturnUri'] = old_instance.analysisReturnUri
        if old_instance.tieringVersion:
            new_instance.additionalInfo['tieringVersion'] = old_instance.tieringVersion
        if old_instance.complexGeneticPhenomena:
            new_instance.additionalInfo['complexGeneticPhenomena'] = str(old_instance.complexGeneticPhenomena)
        if old_instance.cellbaseVersion:
            new_instance.additionalInfo['cellbaseVersion'] = old_instance.cellbaseVersion
        if old_instance.interpretGenome:
            new_instance.additionalInfo['interpretGenome'] = str(old_instance.interpretGenome)

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
        if not isinstance(software_versions, dict):
            software_versions = {}
        software_versions['tiering'] = old_instance.tieringVersion
        new_instance.softwareVersions = software_versions
        new_instance.reportUrl = report_url
        new_instance.comments = comments

        # converts all reported variants
        new_instance.variants = self.convert_collection(
            old_instance.tieredVariants, self._migrate_reported_variant, assembly=assembly)

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
        if assembly is None or interpretation_request_version is None:
            raise MigrationError(
                "Parameters <assembly> and <interpretation_request_version> are required for models earlier than 5.0.0"
            )
        new_instance = self.convert_class(
            self.new_model.InterpretedGenomeRD, old_instance)  # type:self.new_model.InterpretedGenomeRD
        new_instance.interpretationRequestVersion = interpretation_request_version
        new_instance.interpretationService = old_instance.companyName
        new_instance.variants = self.convert_collection(
            old_instance.reportedVariants, self._migrate_reported_variant, assembly=assembly)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretedGenomeRD
        )

    def migrate_clinical_report_rd(self, old_instance, assembly):
        """
        :type old_instance: reports_4_0_0.ClinicalReportRD
        :type assembly: reports_5_0_0.Assembly
        :rtype: reports_5_0_0.ClinicalReportRD
        """
        if assembly is None:
            raise MigrationError("Parameter <assembly> is required to migrate model versions earlier than 5.0.0")

        new_instance = self.convert_class(
            self.new_model.ClinicalReportRD, old_instance)  # :type self.new_model.ClinicalReportRD

        try:
            new_instance.interpretationRequestVersion = self.convert_string_to_integer(
                old_instance.interpretationRequestVersion)
        except MigrationError as ex:
            logging.error("Error converting 'interpretationRequestVersion' to integer from value '{}'".format(
                old_instance.interpretationRequestVersion))
            raise ex
        new_instance.references = old_instance.supportingEvidence
        new_instance.variants = self.convert_collection(
            old_instance.candidateVariants, self._migrate_reported_variant, assembly=assembly)
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
        if assembly is None:
            raise MigrationError(
                "Parameter <assembly> is required to migrate cancer interpretation request to version 5")

        new_instance = self.convert_class(
            self.new_model.CancerInterpretationRequest, old_instance
        )  # :type: reports_5_0_0.CancerInterpretationRequest

        new_instance.interpretationRequestId = old_instance.reportRequestId
        new_instance.interpretationRequestVersion = old_instance.reportVersion
        new_instance.genomeAssembly = assembly
        new_instance.cancerParticipant = self._migrate_cancer_participant(old_participant=old_instance.cancerParticipant)
        if not new_instance.additionalInfo:
            new_instance.additionalInfo = {}
        if old_instance.analysisUri:
            new_instance.additionalInfo['analysisUri'] = old_instance.analysisUri
        if old_instance.analysisVersion:
            new_instance.additionalInfo['analysisVersion'] = old_instance.analysisVersion
        if old_instance.tieringVersion:
            new_instance.additionalInfo['tieringVersion'] = old_instance.tieringVersion
        if old_instance.interpretGenome:
            new_instance.additionalInfo['interpretGenome'] = str(old_instance.interpretGenome)

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

        new_instance.interpretationRequestId = old_instance.reportRequestId
        new_instance.interpretationRequestVersion = old_instance.reportVersion
        new_instance.interpretationService = interpretation_service
        new_instance.referenceDatabasesVersions = reference_database_versions
        if not isinstance(software_versions, dict):
            software_versions = {}
        software_versions['tiering'] = old_instance.tieringVersion
        new_instance.softwareVersions = software_versions
        new_instance.reportUrl = report_url
        new_instance.comments = comments
        participant_id = old_instance.cancerParticipant.individualId
        tumor_samples = old_instance.cancerParticipant.tumourSamples
        germline_samples = old_instance.cancerParticipant.germlineSamples
        if not tumor_samples:
            raise MigrationError("There is no tumour sample to perform the migration")
        elif len(tumor_samples) > 1:
            raise MigrationError("There are several tumour samples, cannot decide which to use '{}'"
                                 .format(str(tumor_samples)))
        sample_ids = {
            'germline_variant': germline_samples[0].sampleId if germline_samples else None,
            'somatic_variant': tumor_samples[0].sampleId
        }
        new_instance.variants = self.convert_collection(
            old_instance.tieredVariants, self._migrate_reported_variant_cancer,
            assembly=assembly, participant_id=participant_id, sample_ids=sample_ids)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.CancerInterpretedGenome
        )

    def migrate_cancer_interpreted_genome(self, old_instance,
                                          assembly, participant_id, sample_ids,
                                          interpretation_request_version, interpretation_service):
        """
        NOTE: we migrate from a model where only one sample and one participant is supported, thus we do not need
        a list of samples or participants
        :type old_instance: reports_4_0_0.CancerInterpretedGenome
        :type assembly: reports_5_0_0.Assembly
        :type participant_id: str
        :type sample_ids: sample_ids: map[str (alleleOrigin)]: str - {'germline_variant': 'LP...', 'somatic_variant': 'LP...'}
        :type interpretation_request_version: int
        :type interpretation_service: str
        :rtype: reports_5_0_0.CancerInterpretedGenome
        """
        self._check_required_parameters(
            assembly=assembly, participant_id=participant_id, sample_ids=sample_ids,
            interpretation_request_version=interpretation_request_version,
            interpretation_service=interpretation_service
        )

        new_instance = self.convert_class(self.new_model.CancerInterpretedGenome, old_instance)  # :type: reports_5_0_0.CancerInterpretedGenome
        new_instance.interpretationRequestId = old_instance.reportRequestId
        new_instance.interpretationRequestVersion = interpretation_request_version
        new_instance.interpretationService = interpretation_service
        new_instance.reportUrl = old_instance.reportUri
        new_instance.variants = self.convert_collection(
            old_instance.reportedVariants, self._migrate_reported_variant_cancer,
            assembly=assembly, participant_id=participant_id, sample_ids=sample_ids)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.CancerInterpretedGenome
        )

    def migrate_cancer_clinical_report(self, old_instance, assembly, participant_id, sample_ids):
        """
        NOTE: we migrate from a model where only one sample and one participant is supported, thus we do not need
        a list of samples or participants
        :type old_instance: reports_4_0_0.ClinicalReportCancer
        :type assembly: reports_5_0_0.Assembly
        :type participant_id: str
        :type sample_ids: map[str (alleleOrigin)]: str - {'germline_variant': 'LP...', 'somatic_variant': 'LP...'}
        :rtype: reports_5_0_0.ClinicalReportCancer
        """
        if not sample_ids or not assembly or not participant_id:
            raise MigrationError("Missing required fields to migrate cancer clinical report from 4.0.0 to 5.0.0")

        new_instance = self.convert_class(
            self.new_model.ClinicalReportCancer, old_instance)  # :type: reports_5_0_0.ClinicalReportCancer
        try:
            new_instance.interpretationRequestVersion = self.convert_string_to_integer(
                old_instance.interpretationRequestVersion)
        except MigrationError as ex:
            logging.error("Error converting 'interpretationRequestVersion' to integer from value '{}'".format(
                old_instance.interpretationRequestVersion))
            raise ex
        new_instance.variants = self.convert_collection(
            old_instance.candidateVariants, self._migrate_reported_variant_cancer,
            assembly=assembly, participant_id=participant_id, sample_ids=sample_ids)

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ClinicalReportCancer
        )

    def _migrate_reported_variant(self, old_instance, assembly, migrate_frequencies=False):
        new_instance = self.convert_class(
            self.new_model.ReportedVariant, old_instance)  # :type: reports_5_0_0.ReportedVariant
        new_instance.variantCoordinates = reports_5_0_0.VariantCoordinates(
            chromosome=old_instance.chromosome,
            position=old_instance.position,
            reference=old_instance.reference,
            alternate=old_instance.alternate,
            assembly=self._migrate_assembly(assembly)
        )
        new_instance.variantCalls = self.convert_collection(
            old_instance.calledGenotypes, self._migrate_called_genotype_to_variant_call, default=[])
        new_instance.reportEvents = self.convert_collection(
            list(zip(old_instance.reportEvents, new_instance.reportEvents)), self._migrate_report_event)
        new_instance.references = old_instance.evidenceIds
        new_instance.alleleOrigins = [reports_5_0_0.AlleleOrigin.germline_variant]
        if migrate_frequencies:
            new_instance.alleleFrequencies = self._migrate_allele_frequencies(
                old_instance.additionalNumericVariantAnnotations)
        # TODO: fields that are not filled: variantAttributes, alleleFrequencies,
        # TODO: dbSnpId, cosmicIds, clinVarIds, genomicChange, cdnaChanges, proteinChanges
        return new_instance

    def _migrate_assembly(self, assembly):
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

    def _migrate_called_genotype_to_variant_call(self, old_instance):
        new_instance = self.convert_class(
            self.new_model.VariantCall, old_instance)  # :type: reports_5_0_0.VariantCall
        new_instance.participantId = old_instance.gelId
        new_instance.zygosity = old_instance.genotype
        new_instance.alleleOrigins = [reports_5_0_0.AlleleOrigin.germline_variant]
        # NOTE: fields that are lost: copyNumber
        # NOTE: fields that cannot be filled: vaf, alleleOrigins
        return new_instance

    def _migrate_report_event(self, report_events):
        old_instance = report_events[0]
        new_instance = report_events[1]
        new_instance.phenotypes = [old_instance.phenotype]
        if old_instance.panelName is not None:
            new_instance.genePanel = self.new_model.GenePanel(
                panelName=old_instance.panelName)
            if old_instance.panelVersion is not None:
                new_instance.genePanel.panelVersion = old_instance.panelVersion
        new_instance.genomicEntities = [self._migrate_genomic_feature(old_instance.genomicFeature)]
        if old_instance.variantClassification is not None:
            old_variant_classification = reports_4_0_0.VariantClassification
            new_clinical_significance = reports_5_0_0.ClinicalSignificance
            map_variant_classification = {
                old_variant_classification.benign_variant: new_clinical_significance.benign,
                old_variant_classification.likely_benign_variant: new_clinical_significance.likely_benign,
                old_variant_classification.variant_of_unknown_clinical_significance:
                    new_clinical_significance.uncertain_significance,
                old_variant_classification.likely_pathogenic_variant: new_clinical_significance.likely_pathogenic,
                old_variant_classification.pathogenic_variant: new_clinical_significance.pathogenic,
                old_variant_classification.not_assessed: None
            }
            clinical_significance = map_variant_classification[old_instance.variantClassification]
            if clinical_significance is not None:
                new_instance.variantClassification = self.new_model.VariantClassification(
                    clinicalSignificance=map_variant_classification[old_instance.variantClassification]
                )
        # NOTE: variant consequences cannot be filled, but it is not nullable so we are creating an empty list
        new_instance.variantConsequences = []
        if new_instance.score == -999.0:    # NOTE: this is a tag value to mark null values in the reverse migration
            new_instance.score = None
        return new_instance

    def _migrate_genomic_feature(self, old_instance):
        new_instance = self.convert_class(self.new_model.GenomicEntity, old_instance)
        new_instance.geneSymbol = old_instance.hgnc
        map_feature_type = {
            reports_4_0_0.FeatureTypes.Transcript: reports_5_0_0.GenomicEntityType.transcript,
            reports_4_0_0.FeatureTypes.RegulatoryRegion: reports_5_0_0.GenomicEntityType.regulatory_region,
            reports_4_0_0.FeatureTypes.Gene: reports_5_0_0.GenomicEntityType.gene
        }
        new_instance.type = map_feature_type[old_instance.featureType]
        return new_instance

    def _migrate_reported_variant_cancer(self, old_instance, assembly, participant_id, sample_ids):
        ne_instance = old_instance.reportedVariantCancer
        new_instance = self.convert_class(self.new_model.ReportedVariantCancer, ne_instance)  # :type: reports_5_0_0.ReportedVariant
        new_instance.variantCoordinates = self.convert_class(reports_5_0_0.VariantCoordinates, ne_instance)
        new_instance.variantCoordinates.assembly = self._migrate_assembly(assembly)
        if old_instance.reportedVariantCancer.cDnaChange:
            new_instance.cdnaChanges = [old_instance.reportedVariantCancer.cDnaChange]
        if ne_instance.proteinChange:
            new_instance.proteinChanges = [ne_instance.proteinChange]

        # NOTE: missing fields: genomicChanges
        sample_id = sample_ids.get(old_instance.alleleOrigins[0], None)
        if not sample_id:
            raise MigrationError('Couldn\'t retrieve Sample ID for {}'.format(old_instance.alleleOrigins[0]))

        # builds up the VariantCall object
        # NOTE: fields that cannot be filled "phaseSet"
        new_instance.variantCalls = [reports_5_0_0.VariantCall(
            depthReference=ne_instance.depthReference,
            depthAlternate=ne_instance.depthAlternate,
            vaf=ne_instance.vaf,
            zygosity=reports_5_0_0.Zygosity.na,
            alleleOrigins=old_instance.alleleOrigins,
            participantId=participant_id,
            sampleId=sample_id
        )]
        if ne_instance.commonAf is not None:
            new_instance.alleleFrequencies = [reports_5_0_0.AlleleFrequency(
                study='genomics_england',
                population='ALL',
                alternateFrequency=self.convert_string_to_float(ne_instance.commonAf)/100
            )]
        # NOTE: some fields cannot be filled: "fdp50", "recurrentlyReported", "others"
        new_instance.variantAttributes = reports_5_0_0.VariantAttributes(
            ihp=ne_instance.ihp
        )
        new_instance.alleleOrigins = old_instance.alleleOrigins
        new_instance.reportEvents = self.convert_collection(
            list(zip(ne_instance.reportEvents, new_instance.reportEvents)), self._migrate_report_event_cancer)
        return new_instance

    def _migrate_report_event_cancer(self, report_events):
        old_instance = report_events[0]
        new_instance = report_events[1]
        new_instance.genomicEntities = [self._migrate_genomic_feature_cancer(old_instance.genomicFeatureCancer)]
        if old_instance.soTerms is not None:
            new_instance.variantConsequences = [reports_5_0_0.VariantConsequence(id=so_term.id, name=so_term.name)
                                                for so_term in old_instance.soTerms]
        if old_instance.actions is not None:
            new_instance.actions = self.convert_collection(
                list(zip(old_instance.actions, new_instance.actions)), self._migrate_action)
        map_role_in_cancer = {
            None: None,
            reports_4_0_0.RoleInCancer.both: [reports_5_0_0.RoleInCancer.both],
            reports_4_0_0.RoleInCancer.oncogene: [reports_5_0_0.RoleInCancer.oncogene],
            reports_4_0_0.RoleInCancer.TSG: [reports_5_0_0.RoleInCancer.tumor_suppressor_gene]
        }
        new_instance.roleInCancer = map_role_in_cancer[old_instance.genomicFeatureCancer.roleInCancer]
        return new_instance

    def _migrate_genomic_feature_cancer(self, old_instance):
        new_instance = self.convert_class(self.new_model.GenomicEntity, old_instance)
        new_instance.type = self.feature_genomic_entity_map[old_instance.featureType]
        new_instance.geneSymbol = old_instance.geneName
        new_instance.otherIds = dict(
            refSeqTranscriptId=old_instance.refSeqTranscriptId, refSeqProteinId=old_instance.refSeqProteinId
        )
        return new_instance

    def _migrate_action(self, actions):
        old_instance = actions[0]
        new_instance = actions[1]
        new_instance.evidenceType = old_instance.actionType
        new_instance.actionType = None
        new_instance.references = old_instance.evidence
        if old_instance.status is not None:
            status = old_instance.status.lower().replace('-', '_')
            if status == reports_5_0_0.ActionStatus.clinical:
                new_instance.status = reports_5_0_0.ActionStatus.clinical
            elif status == reports_5_0_0.ActionStatus.pre_clinical:
                new_instance.status = reports_5_0_0.ActionStatus.pre_clinical
            elif status is not None and status != "":
                raise MigrationError("Action status does not match any known value '{}'".format(status))
        return new_instance

    def _migrate_cancer_participant(self, old_participant):
        part_migrated = self.participant_migrator.migrate_cancer_participant(old_participant)
        return MigrationParticipants103To110().migrate_cancer_participant(part_migrated)

    def _migrate_pedigree(self, old_pedigree):
        part_migrated = self.participant_migrator.migrate_pedigree(old_pedigree)
        return MigrationParticipants103To110().migrate_pedigree(part_migrated)

    @staticmethod
    def _migrate_allele_frequencies(additional_numeric_annotations):
        # NOTE: This is assuming all values in `additionalNumericVariantAnnotations` are frequencies
        frequencies = []
        for pop in additional_numeric_annotations:
            frequencies.append(reports_5_0_0.AlleleFrequency(
                alternateFrequency=additional_numeric_annotations[pop],
                population=pop.split('_')[-1],
                study='_'.join(pop.split('_')[:-1])
            ))
        return frequencies

    @staticmethod
    def _raise_migration_error_for_parameter(parameter):
        raise MigrationError(
            "Missing required field {parameter} to migrate a cancer interpreted genome from 4.0.0 to 5.0.0".format(
                parameter=parameter
            )
        )

    def _check_required_parameters(self, assembly=None, participant_id=None, sample_ids=None,
                                   interpretation_request_version=None, interpretation_service=None):
        if not assembly:
            self._raise_migration_error_for_parameter(parameter='assembly')
        if not participant_id:
            self._raise_migration_error_for_parameter(parameter='participant_id')
        if not sample_ids:
            self._raise_migration_error_for_parameter(parameter='sample_ids')
        if not interpretation_request_version:
            self._raise_migration_error_for_parameter(parameter='interpretation_request_version')
        if not interpretation_service:
            self._raise_migration_error_for_parameter(parameter='interpretation_request_version')

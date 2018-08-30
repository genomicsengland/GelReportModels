import logging

from protocols import reports_4_0_0 as reports_4_0_0
from protocols import reports_5_0_0 as reports_5_0_0
from protocols import opencb_1_3_0 as opencb_1_3_0
from protocols.migration.base_migration import MigrationError, BaseMigrateReports400And500
import itertools


class MigrateReports400To500(BaseMigrateReports400And500):

    old_model = reports_4_0_0
    new_model = reports_5_0_0

    def migrate_interpretation_request_rd(self, old_instance, assembly):
        """
        Migrates an InterpretationRequestRD into an InterpretedGenomeRD, several unexisting fields need to be provided
        :type old_instance: reports_4_0_0.InterpretationRequestRD
        :rtype: reports_5_0_0.InterpretationRequestRD
        """
        if assembly is None:
            raise MigrationError("Parameter <assembly> is required if version is older than 5.0.0")

        new_instance = self.convert_class(self.new_model.InterpretationRequestRD, old_instance)
        new_instance.genomeAssembly = assembly
        new_instance.pedigree.members = self.convert_collection(
            old_instance.pedigree.members, self.migrate_pedigree_member)

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
        new_instance.variants = self.convert_collection(
            old_instance.tieredVariants, self.migrate_reported_variant, assembly=assembly)

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
            old_instance.reportedVariants, self.migrate_reported_variant, assembly=assembly)

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
            old_instance.candidateVariants, self.migrate_reported_variant, assembly=assembly)
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
        new_instance.cancerParticipant = self.migrate_cancer_participant(old_participant=old_instance.cancerParticipant)

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
        new_instance.softwareVersions = software_versions
        new_instance.reportUrl = report_url
        new_instance.comments = comments
        participant_id = old_instance.cancerParticipant.individualId
        tumor_samples = old_instance.cancerParticipant.tumourSamples
        if not tumor_samples:
            raise MigrationError("There is no tumour sample to perform the migration")
        elif len(tumor_samples) > 1:
            raise MigrationError("There are several tumour samples, cannot decide which to use '{}'"
                                 .format(str(tumor_samples)))
        sample_id = tumor_samples[0].sampleId
        new_instance.variants = self.convert_collection(
            old_instance.tieredVariants, self.migrate_reported_variant_cancer,
            assembly=assembly, participant_id=participant_id, sample_id=sample_id)

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
        self.check_required_parameters(
            assembly=assembly, participant_id=participant_id, sample_id=sample_id,
            interpretation_request_version=interpretation_request_version,
            interpretation_service=interpretation_service
        )

        new_instance = self.convert_class(self.new_model.CancerInterpretedGenome, old_instance)  # :type: reports_5_0_0.CancerInterpretedGenome
        new_instance.interpretationRequestId = old_instance.reportRequestId
        new_instance.interpretationRequestVersion = interpretation_request_version
        new_instance.interpretationService = interpretation_service
        new_instance.reportUrl = old_instance.reportUri
        new_instance.variants = self.convert_collection(
            old_instance.reportedVariants, self.migrate_reported_variant_cancer,
            assembly=assembly, participant_id=participant_id, sample_id=sample_id)

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
        if not sample_id or not assembly or not participant_id:
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
            old_instance.candidateVariants, self.migrate_reported_variant_cancer,
            assembly=assembly, participant_id=participant_id, sample_id=sample_id)

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
        new_instance.variantCoordinates = reports_5_0_0.VariantCoordinates(
            chromosome=old_instance.chromosome,
            position=old_instance.position,
            reference=old_instance.reference,
            alternate=old_instance.alternate,
            assembly=self.migrate_assembly(assembly)
        )
        new_instance.variantCalls = self.convert_collection(
            old_instance.calledGenotypes, self.migrate_called_genotype_to_variant_call, default=[])
        new_instance.reportEvents = self.convert_collection(old_instance.reportEvents, self.migrate_report_event)
        new_instance.references = old_instance.evidenceIds
        new_instance.alleleOrigins = [reports_5_0_0.AlleleOrigin.germline_variant]
        if migrate_frequencies:
            new_instance.alleleFrequencies = self.migrate_allele_frequencies(
                old_instance.additionalNumericVariantAnnotations)

        # TODO: fields that are not filled: variantAttributes, alleleFrequencies,
        # TODO: dbSnpId, cosmicIds, clinVarIds, genomicChange, cdnaChanges, proteinChanges

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ReportedVariant
        )

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
        new_instance.participantId = old_instance.gelId
        new_instance.zygosity = old_instance.genotype
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
        new_instance.phenotypes = [old_instance.phenotype]
        if old_instance.panelName is not None:
            new_instance.genePanel = self.new_model.GenePanel(
                panelName=old_instance.panelName)
            if old_instance.panelVersion is not None:
                new_instance.genePanel.panelVersion = old_instance.panelVersion
        new_instance.genomicEntities = [self.migrate_genomic_feature(old_instance.genomicFeature)]
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

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ReportEvent
        )

    def migrate_genomic_feature(self, old_instance):
        """
        # NOTE: some fields cannot be filled: otherIds
        :type old_instance: reports_4_0_0.GenomicFeature
        :rtype reports_5_0_0.GenomicEntity
        :return:
        """
        new_instance = self.convert_class(self.new_model.GenomicEntity, old_instance)
        new_instance.geneSymbol = old_instance.hgnc
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
        :type assembly: str
        :type participant_id: str
        :type sample_id: str
        :rtype reports_5_0_0.ReportedVariantCancer
        :return:
        """
        reported_variant_cancer = old_instance.reportedVariantCancer
        new_instance = self.convert_class(self.new_model.ReportedVariantCancer, reported_variant_cancer)  # :type: reports_5_0_0.ReportedVariant
        new_instance.variantCoordinates = self.convert_class(reports_5_0_0.VariantCoordinates, reported_variant_cancer)
        new_instance.variantCoordinates.assembly = self.migrate_assembly(assembly)
        if old_instance.reportedVariantCancer.cDnaChange:
            new_instance.cdnaChanges = [old_instance.reportedVariantCancer.cDnaChange]
        if reported_variant_cancer.proteinChange:
            new_instance.proteinChanges = [reported_variant_cancer.proteinChange]

        # NOTE: missing fields: genomicChanges

        # builds up the VariantCall object
        # NOTE: fields that cannot be filled "phaseSet"
        new_instance.variantCalls = [reports_5_0_0.VariantCall(
            depthReference=reported_variant_cancer.depthReference,
            depthAlternate=reported_variant_cancer.depthAlternate,
            vaf=reported_variant_cancer.vaf,
            zygosity=reports_5_0_0.Zygosity.na,
            alleleOrigins=old_instance.alleleOrigins,
            participantId=participant_id,
            sampleId=sample_id
        )]
        if reported_variant_cancer.commonAf is not None:
            new_instance.alleleFrequencies = [reports_5_0_0.AlleleFrequency(
                study='genomics_england',
                population='ALL',
                alternateFrequency=self.convert_string_to_float(reported_variant_cancer.commonAf)
            )]
        # NOTE: some fields cannot be filled: "fdp50", "recurrentlyReported", "others"
        new_instance.variantAttributes = reports_5_0_0.VariantAttributes(
            ihp=reported_variant_cancer.ihp
        )
        new_instance.alleleOrigins = old_instance.alleleOrigins
        new_instance.reportEvents = self.convert_collection(
            reported_variant_cancer.reportEvents, self.migrate_report_event_cancer)
        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.ReportedVariantCancer
        )

    def migrate_report_event_cancer(self, old_instance):
        """
        NOTE: fields that cannot be filled are "groupOfVariants", "score", "vendorSpecificScores", "variantClassification"
        :type old_instance: reports_4_0_0.ReportEventCancer
        :rtype reports_5_0_0.ReportEventCancer
        :return:
        """
        new_instance = self.convert_class(self.new_model.ReportEventCancer, old_instance)
        new_instance.genomicEntities = [self.migrate_genomic_feature_cancer(old_instance.genomicFeatureCancer)]
        if old_instance.soTerms is not None:
            new_instance.variantConsequences = [reports_5_0_0.VariantConsequence(id=so_term.id, name=so_term.name)
                                                for so_term in old_instance.soTerms]
        new_instance.actions = self.convert_collection(old_instance.actions, self.migrate_action)
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

    def migrate_genomic_feature_cancer(self, old_instance):
        """
        :type old_instance: reports_4_0_0.GenomicFeatureCancer
        :rtype reports_5_0_0.GenomicEntity
        :return:
        """
        new_instance = self.convert_class(self.new_model.GenomicEntity, old_instance)
        new_instance.type = self.feature_genomic_entity_map[old_instance.featureType]
        new_instance.geneSymbol = old_instance.geneName
        new_instance.otherIds = dict(
            refSeqTranscriptId=old_instance.refSeqTranscriptId, refSeqProteinId=old_instance.refSeqProteinId
        )
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.GenomicEntity)

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
        new_instance.references = old_instance.evidence
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

    def migrate_tumour_sample(self, old_sample, ldp_code):
        ts = self.new_model.TumourSample
        tt = self.new_model.TumourType
        new_sample = self.convert_class(ts, old_sample)  # :type: reports_5_0_0.TumourSample

        tumour_type_enum = [
            tt.PRIMARY, tt.METASTATIC_RECURRENCE, tt.RECURRENCE_OF_PRIMARY_TUMOUR, tt.METASTASES
        ]
        new_sample.tumourType = old_sample.tumourType if old_sample.tumourType in tumour_type_enum else None
        new_sample.tumourId = str(old_sample.tumourId)
        if ldp_code is None:
            raise MigrationError("Cannot migrate '{}' to '{}' having an empty value of 'ldp_code'".format(
                type(old_sample), type(new_sample))
            )
        new_sample.LDPCode = ldp_code

        return self.validate_object(object_to_validate=new_sample, object_type=ts)

    def migrate_germline_sample(self, old_sample, ldp_code):
        gs = self.new_model.GermlineSample
        new_sample = self.convert_class(gs, old_sample)  # :type: reports_5_0_0.GermlineSample
        new_sample.LDPCode = ldp_code
        return self.validate_object(object_to_validate=new_sample, object_type=gs)

    def migrate_cancer_participant(self, old_participant):
        new_participant = self.convert_class(
            self.new_model.CancerParticipant, old_participant
        )  # :type: reports_5_0_0.CancerParticipant

        new_participant.tumourSamples = self.convert_collection(
            old_participant.tumourSamples, self.migrate_tumour_sample, ldp_code=old_participant.LDPCode)
        new_participant.germlineSamples = self.convert_collection(
            old_participant.germlineSamples, self.migrate_germline_sample, ldp_code=old_participant.LDPCode)
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
        new_hpo_term.modifiers = self.migrate_hpo_term_modifiers(old_modifiers=old_hpo_term.modifiers)
        return self.validate_object(object_to_validate=new_hpo_term, object_type=new_object_type)

    def migrate_hpo_term_modifiers(self, old_modifiers):
        if old_modifiers is None:
            return None
        # TODO(Greg): Check real data for whether these keys are used
        laterality_enum = [
            self.new_model.Laterality.RIGHT, self.new_model.Laterality.LEFT, self.new_model.Laterality.UNILATERAL,
            self.new_model.Laterality.BILATERAL,
        ]
        laterality = self.extract_hpo_term_modifier(modifier="laterality", map=old_modifiers, enum=laterality_enum)

        progression_enum = [self.new_model.Progression.PROGRESSIVE, self.new_model.Progression.NONPROGRESSIVE]
        progression = self.extract_hpo_term_modifier(modifier="progression", map=old_modifiers, enum=progression_enum)

        severity_enum = [
            self.new_model.Severity.BORDERLINE, self.new_model.Severity.MILD, self.new_model.Severity.MODERATE,
            self.new_model.Severity.SEVERE, self.new_model.Severity.PROFOUND,
        ]
        severity = self.extract_hpo_term_modifier(modifier="severity", map=old_modifiers, enum=severity_enum)

        spatial_enum = [
            self.new_model.SpatialPattern.DISTAL, self.new_model.SpatialPattern.GENERALIZED,
            self.new_model.SpatialPattern.LOCALIZED, self.new_model.SpatialPattern.PROXIMAL,
        ]
        spatial_pattern = self.extract_hpo_term_modifier(modifier="spatial_pattern", map=old_modifiers, enum=spatial_enum)

        new_modifier = self.new_model.HpoTermModifiers(
            laterality=laterality,
            progression=progression,
            severity=severity,
            spatialPattern=spatial_pattern,
        )
        return self.validate_object(object_to_validate=new_modifier, object_type=self.new_model.HpoTermModifiers)

    @staticmethod
    def extract_hpo_term_modifier(modifier, map, enum):
        new_modifier = map.get(modifier, "").upper()
        return new_modifier if new_modifier in enum else None

    def migrate_pedigree_member(self, old_member):
        new_object_type = self.new_model.PedigreeMember
        new_member = self.convert_class(target_klass=new_object_type, instance=old_member)
        new_member.disorderList = self.convert_collection(old_member.disorderList, self.migrate_disorder)
        new_member.hpoTermList = self.convert_collection(old_member.hpoTermList, self.migrate_hpo_term)
        return self.validate_object(object_to_validate=new_member, object_type=new_object_type)

    @staticmethod
    def migrate_allele_frequencies(additionalNumericVariantAnnotations):
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

    @staticmethod
    def raise_migration_error_for_parameter(parameter):
        raise MigrationError(
            "Missing required field {parameter} to migrate a cancer interpreted genome from 4.0.0 to 5.0.0".format(
                parameter=parameter
            )
        )

    def check_required_parameters(self, assembly=None, participant_id=None, sample_id=None,
                                  interpretation_request_version=None, interpretation_service=None):
        if not assembly:
            self.raise_migration_error_for_parameter(parameter='assembly')
        if not participant_id:
            self.raise_migration_error_for_parameter(parameter='participant_id')
        if not sample_id:
            self.raise_migration_error_for_parameter(parameter='sample_id')
        if not interpretation_request_version:
            self.raise_migration_error_for_parameter(parameter='interpretation_request_version')
        if not interpretation_service:
            self.raise_migration_error_for_parameter(parameter='interpretation_request_version')
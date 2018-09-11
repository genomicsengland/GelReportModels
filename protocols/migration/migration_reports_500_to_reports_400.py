import logging
import distutils.util

from protocols import reports_4_0_0 as reports_4_0_0
from protocols import reports_5_0_0 as reports_5_0_0
from protocols.migration.base_migration import BaseMigrateReports400And500
from protocols.migration.base_migration import MigrationError
from protocols.migration import MigrateParticipant110To100


class MigrateReports500To400(BaseMigrateReports400And500):

    old_model = reports_5_0_0
    new_model = reports_4_0_0

    cip_short_codes = {
        'omicia': 'OPA',
        'congenica': 'SAP',
        'nextcode': 'CSA',
        'illumina': 'ILMN',
        'genomics_england': 'GEL',
        'exomiser': 'EXM'
    }
    tier_map = {
        old_model.Tier.NONE: new_model.Tier.NONE,
        old_model.Tier.TIER1: new_model.Tier.TIER1,
        old_model.Tier.TIER2: new_model.Tier.TIER2,
        old_model.Tier.TIER3: new_model.Tier.TIER3,
        old_model.Tier.TIER4: new_model.Tier.NONE,
        old_model.Tier.TIER5: new_model.Tier.NONE,
    }
    genotype_map = {
        old_model.Zygosity.reference_homozygous: new_model.Zygosity.reference_homozygous,
        old_model.Zygosity.heterozygous: new_model.Zygosity.heterozygous,
        old_model.Zygosity.alternate_homozygous: new_model.Zygosity.alternate_homozygous,
        old_model.Zygosity.missing: new_model.Zygosity.missing,
        old_model.Zygosity.half_missing_reference: new_model.Zygosity.half_missing_reference,
        old_model.Zygosity.half_missing_alternate: new_model.Zygosity.half_missing_alternate,
        old_model.Zygosity.alternate_hemizigous: new_model.Zygosity.alternate_hemizigous,
        old_model.Zygosity.reference_hemizigous: new_model.Zygosity.reference_hemizigous,
        old_model.Zygosity.unk: new_model.Zygosity.unk,
    }
    feature_type_map = {
        old_model.GenomicEntityType.transcript: new_model.FeatureTypes.Transcript,
        old_model.GenomicEntityType.regulatory_region: new_model.FeatureTypes.RegulatoryRegion,
        old_model.GenomicEntityType.gene: new_model.FeatureTypes.Gene,
    }
    variant_classification_map = {
        old_model.ClinicalSignificance.benign: new_model.VariantClassification.benign_variant,
        old_model.ClinicalSignificance.likely_benign: new_model.VariantClassification.likely_benign_variant,
        old_model.ClinicalSignificance.VUS: new_model.VariantClassification.variant_of_unknown_clinical_significance,
        old_model.ClinicalSignificance.uncertain_significance:
            new_model.VariantClassification.variant_of_unknown_clinical_significance,
        old_model.ClinicalSignificance.likely_pathogenic: new_model.VariantClassification.likely_pathogenic_variant,
        old_model.ClinicalSignificance.pathogenic: new_model.VariantClassification.pathogenic_variant,
    }

    def migrate_interpretation_request_rd(self, old_instance, old_ig):
        """
        Migrates a reports_5_0_0.InterpretationRequestRD into a reports_4_0_0.InterpretationRequestRD
        :type old_instance: reports_5_0_0.InterpretationRequestRD
        :type old_ig: reports_5_0_0.InterpretedGenomeRD
        :rtype: reports_4_0_0.InterpretationRequestRD
        """
        new_instance = self.convert_class(self.new_model.InterpretationRequestRD, old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        new_instance.genomeAssemblyVersion = old_instance.genomeAssembly
        # ensure null lists of files are not passing through
        if new_instance.bams is None:
            new_instance.bams = []
        if new_instance.vcfs is None:
            new_instance.vcfs = []
        # grabs the list of variants from the interpreted genome
        new_instance.tieredVariants = self.convert_collection(old_ig.variants, self._migrate_reported_variant)
        new_instance.tieringVersion = old_ig.softwareVersions.get("tiering", "")
        new_instance.analysisVersion = ''
        new_instance.analysisReturnUri = ''
        if old_instance.additionalInfo:
            new_instance.analysisVersion = old_instance.additionalInfo.get('analysisVersion') or ''
            new_instance.analysisReturnUri = old_instance.additionalInfo.get('analysisReturnUri', '')
            new_instance.tieringVersion = old_instance.additionalInfo.get('tieringVersion', '')
            new_instance.complexGeneticPhenomena = old_instance.additionalInfo.get('complexGeneticPhenomena')
            new_instance.cellbaseVersion = old_instance.additionalInfo.get('cellbaseVersion', '')
            new_instance.interpretGenome = bool(distutils.util.strtobool(old_instance.additionalInfo.get('interpretGenome', 'false')))

        if not old_instance.pedigree:
            raise MigrationError("Cannot reverse migrate an Interpretation Request for RD with null pedigree")
        new_instance.pedigree = MigrateParticipant110To100().migrate_pedigree(old_instance.pedigree)

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD)

    def migrate_interpreted_genome_rd(self, old_instance, cip=None):
        """
        :type old_instance: reports_5_0_0.InterpretedGenomeRD
        :type cip:
        :rtype: reports_4_0_0.InterpretedGenomeRD
        """
        new_instance = self.convert_class(self.new_model.InterpretedGenomeRD, old_instance)  # :type self.new_model.InterpretedGenomeRD
        new_instance.versionControl = self.new_model.ReportVersionControl()
        new_instance.analysisId = str(old_instance.interpretationRequestVersion)
        new_instance.companyName = old_instance.interpretationService
        if new_instance.reportUrl is None:
            new_instance.reportUrl = ''
        new_instance.reportUri = "/gel/returns/{cip_short}-{ir_id}-{ir_version}".format(
            cip_short=self.cip_short_codes.get(cip),
            ir_id=old_instance.interpretationRequestId,
            ir_version=old_instance.interpretationRequestVersion) if cip else ''
        new_instance.reportedVariants = self.convert_collection(old_instance.variants, self._migrate_reported_variant)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ClinicalReportRD)

    def migrate_clinical_report_rd(self, old_instance):
        """
        :type old_instance: reports_5_0_0.ClinicalReportRD
        :rtype: reports_4_0_0.ClinicalReportRD
        """
        new_instance = self.convert_class(self.new_model.ClinicalReportRD, old_instance)  # :type self.new_model.ClinicalReportRD
        # type of interpretationRequestVersion has been changed from int to str
        new_instance.interpretationRequestVersion = str(old_instance.interpretationRequestVersion)
        # references has been renamed to supportingEvidence
        new_instance.supportingEvidence = old_instance.references
        new_instance.candidateVariants = self.convert_collection(old_instance.variants, self._migrate_reported_variant)
        new_instance.additionalAnalysisPanels = self.convert_collection(
            old_instance.additionalAnalysisPanels, self._migrate_analysis_panel)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ClinicalReportRD)

    def migrate_exit_questionnaire_rd(self, old_instance):
        """
        :type old_instance: reports_5_0_0.RareDiseaseExitQuestionnaire
        :rtype: reports_4_0_0.RareDiseaseExitQuestionnaire
        """
        new_instance = self.convert_class(self.new_model.RareDiseaseExitQuestionnaire, old_instance)  # :type self.new_model.RareDiseaseExitQuestionnaire
        return self.validate_object(object_to_validate=new_instance,
                                    object_type=self.new_model.RareDiseaseExitQuestionnaire)

    def migrate_cancer_interpreted_genome(self, old_instance):
        """
        :type old_instance: reports_5_0_0.CancerInterpretedGenome
        :rtype: reports_4_0_0.CancerInterpretedGenome
        """
        new_instance = self.convert_class(self.new_model.CancerInterpretedGenome, old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        new_instance.reportedVariants = self.convert_collection(
            old_instance.variants, self._migrate_reported_variant_cancer_to_reported_somatic_variant)
        new_instance.reportRequestId = old_instance.interpretationRequestId
        new_instance.reportUri = old_instance.reportUrl or ''
        new_instance.analysisId = ''
        new_instance.reportedStructuralVariants = []

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.CancerInterpretedGenome
        )

    def migrate_interpretation_request_cancer_plus_cancer_interpreted_genome(self, old_instance, old_interpreted_genome):
        """
        :type old_instance: reports_5_0_0.CancerInterpretationRequest
        :type old_interpreted_genome: reports_5_0_0.CancerInterpretedGenome
        :rtype: reports_4_0_0.CancerInterpretationRequest
        """
        new_instance = self.convert_class(target_klass=self.new_model.CancerInterpretationRequest, instance=old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        new_instance.reportRequestId = old_instance.interpretationRequestId
        new_instance.reportVersion = old_instance.interpretationRequestVersion
        new_instance.interpretGenome = True
        if new_instance.bams is None:
            new_instance.bams = []
        if new_instance.vcfs is None:
            new_instance.vcfs = []
        if new_instance.bigWigs is None:
            new_instance.bigWigs = []
        if old_instance.cancerParticipant:
            new_instance.cancerParticipant = MigrateParticipant110To100().migrate_cancer_participant(
                old_instance=old_instance.cancerParticipant
            )
        else:
            # default empty object as it is non nullable
            new_instance.cancerParticipant = self.new_model.CancerParticipant(
                readyForAnalysis=True,
                individualId="",
                sex=self.new_model.Sex.UNKNOWN,
                tumourSamples=[],
                germlineSamples=[])
        new_instance.structuralTieredVariants = []
        new_instance.analysisVersion = ''
        new_instance.analysisUri = ''
        if old_instance.additionalInfo:
            new_instance.analysisVersion = old_instance.additionalInfo.get('analysisVersion') or ''
            new_instance.analysisUri = old_instance.additionalInfo.get('analysisUri', '')
            new_instance.interpretGenome = bool(distutils.util.strtobool(old_instance.additionalInfo.get('interpretGenome', 'false')))
        new_instance.tieringVersion = old_interpreted_genome.softwareVersions.get("tiering", '')
        new_instance.tieredVariants = self.convert_collection(
            old_interpreted_genome.variants, self._migrate_reported_variant_cancer_to_reported_somatic_variant)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.CancerInterpretationRequest)

    def migrate_cancer_clinical_report(self, old_instance):
        """
        :type old_instance: reports_5_0_0.ClinicalReportCancer
        :rtype: reports_4_0_0.ClinicalReportCancer
        """
        new_instance = self.convert_class(target_klass=self.new_model.ClinicalReportCancer, instance=old_instance)
        new_instance.interpretationRequestVersion = str(old_instance.interpretationRequestVersion)
        new_instance.genePanelsCoverage = {}
        new_instance.candidateVariants = self.convert_collection(
            old_instance.variants, self._migrate_reported_variant_cancer_to_reported_somatic_variant)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ClinicalReportCancer)

    def _migrate_analysis_panel(self, old_panel):
        new_panel = self.new_model.AdditionalAnalysisPanel(
            panelVersion=old_panel.panel.panelVersion,
            panelName=old_panel.panel.panelName,
            specificDisease=old_panel.specificDisease,
        )
        return new_panel

    def _migrate_reported_variant(self, old_reported_variant):
        new_instance = self.convert_class(self.new_model.ReportedVariant, old_reported_variant)
        new_instance.chromosome = old_reported_variant.variantCoordinates.chromosome
        new_instance.position = old_reported_variant.variantCoordinates.position
        new_instance.reference = old_reported_variant.variantCoordinates.reference
        new_instance.alternate = old_reported_variant.variantCoordinates.alternate
        new_instance.evidenceIds = old_reported_variant.references
        new_instance.calledGenotypes = self.convert_collection(
            old_reported_variant.variantCalls, self._migrate_variant_call_to_called_genotype)
        new_instance.reportEvents = self.convert_collection(
            list(zip(old_reported_variant.reportEvents, new_instance.reportEvents)), self._migrate_report_event)
        new_instance.additionalNumericVariantAnnotations = self._merge_annotations_and_frequencies(
            old_reported_variant.additionalNumericVariantAnnotations, old_reported_variant.alleleFrequencies,
        )
        return new_instance

    @staticmethod
    def _merge_annotations_and_frequencies(numeric_annotations, allele_frequencies):
        if numeric_annotations is None:
            numeric_annotations = {}
        if not isinstance(numeric_annotations, dict):
            raise MigrationError("additionalNumericVariantAnnotations should be dict but is: {}".format(numeric_annotations))
        if allele_frequencies is not None:
            for af in allele_frequencies:
                annotation_key = "{}:{}".format(af.study, af.population)
                if annotation_key in numeric_annotations:
                    logging.warning(
                        "{} already exists in numeric_annotations with value {} instead of {}".format(
                            annotation_key, numeric_annotations.get(annotation_key), af.alternateFrequency
                        )
                    )
                else:
                    numeric_annotations["{}:{}".format(af.study, af.population)] = af.alternateFrequency
        return numeric_annotations

    def _migrate_genomic_entity_to_feature(self, entity):
        new_instance = self.convert_class(self.new_model.GenomicFeature, entity)
        feature_type = self.feature_type_map.get(entity.type, self.new_model.FeatureTypes.Gene)
        if entity.type not in self.feature_type_map.keys():
            logging.warning(
                "{} can not be migrated to a feature type, as it is not one of: {} so is being migrated to {}".format(
                    entity.type, self.feature_type_map.keys(), self.new_model.FeatureTypes.Gene
                )
            )
        new_instance.featureType = feature_type
        new_instance.hgnc = entity.geneSymbol
        return new_instance

    def _migrate_report_event(self, report_events):
        old_instance = report_events[0]
        new_instance = report_events[1]
        new_instance.phenotype = ','.join(old_instance.phenotypes)
        if old_instance.genePanel is not None:
            if hasattr(old_instance.genePanel, 'panelName') and hasattr(old_instance.genePanel, 'panelVersion'):
                new_instance.panelName = old_instance.genePanel.panelName
                new_instance.panelVersion = old_instance.genePanel.panelVersion
        if isinstance(old_instance.genomicEntities, list):
            if old_instance.genomicEntities:
                first_genomic_entity = old_instance.genomicEntities[0]
                new_instance.genomicFeature = self._migrate_genomic_entity_to_feature(entity=first_genomic_entity)
                if len(old_instance.genomicEntities) > 1:
                    logging.warning("{} genomic entities are being lost in the migration".format(len(old_instance.genomicEntities)-1))
        if old_instance.variantClassification:
            new_instance.variantClassification = self.variant_classification_map.get(
                old_instance.variantClassification.clinicalSignificance,
                self.new_model.VariantClassification.not_assessed
            )
        # NOTE: fields changing their null state
        if new_instance.score is None:
            new_instance.score = -999.0  # NOTE: this is a tag value so we know this was null for forward migration
        if new_instance.penetrance is None:
            new_instance.penetrance = self.new_model.Penetrance.complete
        new_instance.tier = self.tier_map[old_instance.tier] if old_instance.tier else None
        return new_instance

    def _migrate_variant_call_to_called_genotype(self, variant_call):
        new_instance = self.convert_class(self.new_model.CalledGenotype, variant_call)
        genotype = self.genotype_map.get(variant_call.zygosity, self.new_model.Zygosity.unk)
        if variant_call.zygosity != genotype:
            logging.warning("Can not migrate variant call to genotype when zygosity is: {} so migrating to {}".format(
                variant_call.zygosity, self.new_model.Zygosity.unk,
            ))
        new_instance.genotype = genotype
        new_instance.gelId = variant_call.participantId
        return new_instance

    def _migrate_reported_variant_cancer_to_reported_somatic_variant(self, old_variant):
        new_instance = self.convert_class(target_klass=self.new_model.ReportedSomaticVariants, instance=old_variant)
        new_instance.reportedVariantCancer = self._migrate_reported_variant_cancer(old_rvc=old_variant)
        return new_instance

    def _migrate_reported_variant_cancer(self, old_rvc):
        new_instance = self.convert_class(target_klass=self.new_model.ReportedVariantCancer, instance=old_rvc)
        if old_rvc.cdnaChanges:
            new_instance.cDnaChange = next((e for e in old_rvc.cdnaChanges), None)
        if old_rvc.proteinChanges:
            new_instance.proteinChange = next((e for e in old_rvc.proteinChanges), None)
        new_instance.reportEvents = self.convert_collection(
            list(zip(old_rvc.reportEvents, new_instance.reportEvents)), self._migrate_report_event_cancer)
        new_instance.chromosome = old_rvc.variantCoordinates.chromosome
        new_instance.position = old_rvc.variantCoordinates.position
        new_instance.reference = old_rvc.variantCoordinates.reference
        new_instance.alternate = old_rvc.variantCoordinates.alternate
        first_variant_call = old_rvc.variantCalls[0]
        if first_variant_call:
            new_instance.depthReference = first_variant_call.depthReference
            new_instance.depthAlternate = first_variant_call.depthAlternate
            new_instance.vaf = first_variant_call.vaf
            new_instance.depthReference = first_variant_call.depthReference
            if new_instance.additionalTextualVariantAnnotations is None:
                new_instance.additionalTextualVariantAnnotations = {}
            new_instance.additionalTextualVariantAnnotations['zygosity'] = first_variant_call.zygosity
            new_instance.additionalTextualVariantAnnotations['sampleId'] = first_variant_call.sampleId
            new_instance.additionalTextualVariantAnnotations['participantId'] = first_variant_call.participantId
            if new_instance.additionalNumericVariantAnnotations is None:
                new_instance.additionalNumericVariantAnnotations = {}
            if first_variant_call.phaseSet is not None:
                new_instance.additionalNumericVariantAnnotations['phaseSet'] = float(first_variant_call.phaseSet)
        if old_rvc.variantAttributes:
            new_instance.ihp = old_rvc.variantAttributes.ihp
            if new_instance.additionalTextualVariantAnnotations is None:
                new_instance.additionalTextualVariantAnnotations = {}
            if old_rvc.variantAttributes.recurrentlyReported is not None:
                new_instance.additionalTextualVariantAnnotations['recurrentlyReported'] = \
                    str(old_rvc.variantAttributes.recurrentlyReported)
            if old_rvc.variantAttributes.fdp50 is not None:
                new_instance.additionalTextualVariantAnnotations['fdp50'] = old_rvc.variantAttributes.fdp50
            if old_rvc.variantAttributes.others:
                new_instance.additionalTextualVariantAnnotations.update(old_rvc.variantAttributes.others)
        if old_rvc.alleleFrequencies is not None:
            common_afs = [af.alternateFrequency for af in old_rvc.alleleFrequencies
                          if af.study == 'genomics_england' and af.population == 'ALL']
            if common_afs:
                new_instance.commonAf = int(round(float(common_afs[0])*100))
        return new_instance

    def _migrate_report_event_cancer(self, report_events):
        old_instance = report_events[0]
        new_instance = report_events[1]
        new_instance.tier = self.tier_map.get(old_instance.tier)
        new_instance.soTerms = self.convert_collection(
            old_instance.variantConsequences, self._migrate_variant_consequence_to_so_term)
        new_instance.genomicFeatureCancer = self._migrate_genomic_entities_to_genomic_feature_cancer(
            genomic_entities=old_instance.genomicEntities,
        )
        map_role_in_cancer = {
            None: None,
            reports_5_0_0.RoleInCancer.both: reports_4_0_0.RoleInCancer.both,
            reports_5_0_0.RoleInCancer.oncogene: reports_4_0_0.RoleInCancer.oncogene,
            reports_5_0_0.RoleInCancer.tumor_suppressor_gene: reports_4_0_0.RoleInCancer.TSG
        }
        if old_instance.roleInCancer:
            new_instance.genomicFeatureCancer.roleInCancer = map_role_in_cancer[old_instance.roleInCancer[0]]
        if old_instance.actions is not None:
            new_instance.actions = self.convert_collection(
                list(zip(old_instance.actions, new_instance.actions)), self._migrate_action)
        return new_instance

    def _migrate_variant_consequence_to_so_term(self, vc):
        new_instance = self.new_model.SoTerm(id=vc.id)
        new_instance.name = vc.name if vc.name else ""
        return new_instance

    def _migrate_genomic_entities_to_genomic_feature_cancer(self, genomic_entities):
        genomic_entity = next((ge for ge in genomic_entities), self.old_model.GenomicEntity(
            type=self.old_model.GenomicEntityType.gene, ensemblId=""))
        new_instance = self.convert_class(target_klass=self.new_model.GenomicFeatureCancer, instance=genomic_entity)
        new_instance.featureType = self._migrate_genomic_entity_type_to_feature_type(old_type=genomic_entity.type)
        new_instance.geneName = genomic_entity.geneSymbol
        if new_instance.geneName is None:
            new_instance.geneName = ""
        if genomic_entity.otherIds:
            new_instance.refSeqTranscriptId = genomic_entity.otherIds.get("refSeqTranscriptId", "")
            if new_instance.refSeqTranscriptId == "":
                logging.warning(msg="refSeqTranscriptId not contained within otherIds in reverse migration")
            new_instance.refSeqProteinId = genomic_entity.otherIds.get("refSeqProteinId", "")
            if new_instance.refSeqProteinId == "":
                logging.warning(msg="refSeqProteinId not contained within otherIds in reverse migration")
        if new_instance.refSeqTranscriptId is None:
            new_instance.refSeqTranscriptId = ""
        if new_instance.refSeqProteinId is None:
            new_instance.refSeqProteinId = ""
        return new_instance

    def _migrate_genomic_entity_type_to_feature_type(self, old_type):

        if old_type not in self.feature_type_map.keys():
            msg = "GenomicEntityType: {ge_type} is being replaced with {rep} as an equivalent does not exist "
            msg += "in reports_4_0_0 FeatureTypes"
            logging.warning(msg=msg.format(ge_type=old_type, rep=self.new_model.FeatureTypes.Gene))
        return self.feature_type_map.get(old_type, self.new_model.FeatureTypes.Gene)

    def _migrate_action(self, actions):
        old_instance = actions[0]
        new_instance = actions[1]
        new_instance.actionType = old_instance.evidenceType
        new_instance.evidenceType = None
        new_instance.evidence = old_instance.references
        return new_instance

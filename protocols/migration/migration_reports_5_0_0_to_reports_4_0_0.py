import logging

from protocols import reports_4_0_0 as reports_4_0_0
from protocols import reports_5_0_0 as reports_5_0_0
from protocols.migration.base_migration import BaseMigrateReports400And500
from protocols.migration.base_migration import MigrationError
from protocols.migration.participants import MigrationParticipants103To100
from protocols.migration.migration_participant_1_1_0_to_participant_1_0_0 import MigrateParticipant110To100
from protocols.migration.migration_participant_1_1_0_to_participant_1_0_3 import MigrateParticipant110To103
from protocols.migration.participants import MigrationParticipants110To100


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

    def migrate_interpretation_request_rd(self, old_instance, old_ig, cip=None):
        """
        Migrates a reports_5_0_0.InterpretationRequestRD into a reports_4_0_0.InterpretationRequestRD
        :type old_instance: reports_5_0_0.InterpretationRequestRD
        :type old_ig: reports_5_0_0.InterpretedGenomeRD
        :param cip: this is used to build the field `analysisReturnUri`, it will be empty if not provided
        :type cip: str
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
        new_instance.tieredVariants = self.migrate_reported_variants(old_reported_variants=old_ig.variants)
        new_instance.tieringVersion = old_ig.softwareVersions.get("tiering", "")
        new_instance.complexGeneticPhenomena = None  # cannot fill this one, but it has never been used
        new_instance.analysisReturnUri = "/gel/returns/{cip_short}-{ir_id}-{ir_version}".format(
            cip_short=self.cip_short_codes.get(cip),
            ir_id=old_instance.interpretationRequestId,
            ir_version=old_instance.interpretationRequestVersion) if cip else ""
        new_instance.analysisVersion = "1"  # it is always 1, so it can be hard-coded here
        if not old_instance.pedigree:
            raise MigrationError("Cannot reverse migrate an Interpretation Request for RD with null pedigree")
        new_instance.pedigree = MigrationParticipants110To100().migrate_pedigree(old_instance.pedigree)

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD)

    def migrate_interpreted_genome_rd(self, old_instance):
        """
        :type old_instance: reports_5_0_0.InterpretedGenomeRD
        :rtype: reports_4_0_0.InterpretedGenomeRD
        """
        new_instance = self.convert_class(self.new_model.InterpretedGenomeRD, old_instance)  # :type self.new_model.InterpretedGenomeRD
        new_instance.versionControl = self.new_model.ReportVersionControl()
        new_instance.analysisId = str(old_instance.interpretationRequestVersion)
        new_instance.companyName = old_instance.interpretationService
        if new_instance.reportUrl is None:
            new_instance.reportUrl = ""
        new_instance.reportUri = ""
        new_instance.reportedVariants = self.migrate_reported_variants(old_reported_variants=old_instance.variants)
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
        new_instance.candidateVariants = self.migrate_reported_variants(old_reported_variants=old_instance.variants)
        new_instance.additionalAnalysisPanels = self.migrate_analysis_panels(
            old_panels=old_instance.additionalAnalysisPanels)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ClinicalReportRD)

    def migrate_exit_questionnaire_rd(self, old_instance):
        """
        :type old_instance: reports_5_0_0.RareDiseaseExitQuestionnaire
        :rtype: reports_4_0_0.RareDiseaseExitQuestionnaire
        """
        new_instance = self.convert_class(self.new_model.RareDiseaseExitQuestionnaire, old_instance)  # :type self.new_model.RareDiseaseExitQuestionnaire
        return self.validate_object(object_to_validate=new_instance,
                                    object_type=self.new_model.RareDiseaseExitQuestionnaire)

    def migrate_analysis_panels(self, old_panels):
        if not old_panels:
            return old_panels
        return [self.migrate_analysis_panel(old_panel=panel) for panel in old_panels]

    def migrate_analysis_panel(self, old_panel):
        new_panel = self.new_model.AdditionalAnalysisPanel(
            panelVersion=old_panel.panel.panelVersion,
            panelName=old_panel.panel.panelName,
            specificDisease=old_panel.specificDisease,
        )
        return self.validate_object(object_to_validate=new_panel, object_type=self.new_model.AdditionalAnalysisPanel)

    def migrate_reported_variants(self, old_reported_variants):
        if old_reported_variants is None:
            return old_reported_variants
        return [self.migrate_reported_variant(old_reported_variant=old_variant) for old_variant in old_reported_variants]

    def migrate_reported_variant(self, old_reported_variant):
        new_reported_variant = self.new_model.ReportedVariant(
            dbSnpId=old_reported_variant.dbSnpId,
            chromosome=old_reported_variant.variantCoordinates.chromosome,
            position=old_reported_variant.variantCoordinates.position,
            reference=old_reported_variant.variantCoordinates.reference,
            alternate=old_reported_variant.variantCoordinates.alternate,
            additionalTextualVariantAnnotations=old_reported_variant.additionalTextualVariantAnnotations,
            evidenceIds=old_reported_variant.references,
            comments=old_reported_variant.comments,
        )

        new_reported_variant.calledGenotypes = self.migrate_variant_calls_to_called_genotypes(old_reported_variant.variantCalls)

        new_reported_variant.reportEvents = self.migrate_report_events(old_reported_variant.reportEvents)

        new_reported_variant.additionalNumericVariantAnnotations = self.merge_annotations_and_frequencies(
            old_reported_variant.additionalNumericVariantAnnotations, old_reported_variant.alleleFrequencies,
        )
        return self.validate_object(object_to_validate=new_reported_variant, object_type=self.new_model.ReportedVariant)

    @staticmethod
    def merge_annotations_and_frequencies(numeric_annotations, allele_frequencies):
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

    def migrate_genomic_entity_to_feature(self, entity):
        feature_type_map = {
            self.old_model.GenomicEntityType.regulatory_region: self.new_model.FeatureTypes.RegulatoryRegion,
            self.old_model.GenomicEntityType.gene: self.new_model.FeatureTypes.Gene,
            self.old_model.GenomicEntityType.transcript: self.new_model.FeatureTypes.Transcript,
        }
        feature_type = feature_type_map.get(entity.type, self.new_model.FeatureTypes.Gene)
        if feature_type != entity.type:
            logging.warning(
                "{} can not be migrated to a feature type, as it is not one of: {} so is being migrated to {}".format(
                    entity.type, feature_type_map.keys(), self.new_model.FeatureTypes.Gene
                )
            )
        genomic_feature = self.new_model.GenomicFeature(
            featureType=feature_type,
            ensemblId=entity.ensemblId,
            hgnc=entity.geneSymbol,
            otherIds=entity.otherIds,
        )
        return self.validate_object(object_to_validate=genomic_feature, object_type=self.new_model.GenomicFeature)

    def migrate_report_event(self, old_report_event):
        new_report_event = self.convert_class(self.new_model.ReportEvent, old_report_event)

        new_report_event.phenotype = ','.join(old_report_event.phenotypes)

        if old_report_event.genePanel is not None:
            if hasattr(old_report_event.genePanel, 'panelName') and hasattr(old_report_event.genePanel, 'panelVersion'):
                new_report_event.panelName = old_report_event.genePanel.panelName
                new_report_event.panelVersion = old_report_event.genePanel.panelVersion
        if isinstance(old_report_event.genomicEntities, list):
            if old_report_event.genomicEntities:
                first_genomic_entity = old_report_event.genomicEntities[0]
                new_report_event.genomicFeature = self.migrate_genomic_entity_to_feature(entity=first_genomic_entity)
                if len(old_report_event.genomicEntities) > 1:
                    logging.warning("{} genomic entities are being lost in the migration".format(len(old_report_event.genomicEntities)-1))

        variant_classification_map = {
            self.old_model.ClinicalSignificance.benign: self.new_model.VariantClassification.benign_variant,
            self.old_model.ClinicalSignificance.likely_benign: self.new_model.VariantClassification.likely_benign_variant,
            self.old_model.ClinicalSignificance.VUS: self.new_model.VariantClassification.variant_of_unknown_clinical_significance,
            self.old_model.ClinicalSignificance.likely_pathogenic: self.new_model.VariantClassification.likely_pathogenic_variant,
            self.old_model.ClinicalSignificance.pathogenic: self.new_model.VariantClassification.pathogenic_variant,
        }
        if old_report_event.variantClassification:
            new_report_event.variantClassification = variant_classification_map.get(
                old_report_event.variantClassification.clinicalSignificance,
                self.new_model.VariantClassification.not_assessed
            )

        # NOTE: fields changing their null state
        new_report_event.score = -999.0  # NOTE: this is a tag value so we know this was null for forward migration
        if new_report_event.penetrance is None:
            new_report_event.penetrance = self.new_model.Penetrance.complete

        new_report_event.tier = self.tier_map[old_report_event.tier] if old_report_event.tier else self.new_model.Tier.NONE

        return self.validate_object(object_to_validate=new_report_event, object_type=self.new_model.ReportEvent)

    def migrate_report_events(self, old_report_events):
        return [
            self.migrate_report_event(old_report_event=old_report_event)
            for old_report_event in old_report_events
        ]

    def migrate_variant_calls_to_called_genotypes(self, old_variant_calls):
        return [
            self.migrate_variant_call_to_called_genotype(variant_call=variant_call)
            for variant_call in old_variant_calls
        ]

    def migrate_variant_call_to_called_genotype(self, variant_call):

        genotype_map = {
            self.old_model.Zygosity.reference_homozygous: self.new_model.Zygosity.reference_homozygous,
            self.old_model.Zygosity.heterozygous: self.new_model.Zygosity.heterozygous,
            self.old_model.Zygosity.alternate_homozygous: self.new_model.Zygosity.alternate_homozygous,
            self.old_model.Zygosity.missing: self.new_model.Zygosity.missing,
            self.old_model.Zygosity.half_missing_reference: self.new_model.Zygosity.half_missing_reference,
            self.old_model.Zygosity.half_missing_alternate: self.new_model.Zygosity.half_missing_alternate,
            self.old_model.Zygosity.alternate_hemizigous: self.new_model.Zygosity.alternate_hemizigous,
            self.old_model.Zygosity.reference_hemizigous: self.new_model.Zygosity.reference_hemizigous,
            self.old_model.Zygosity.unk: self.new_model.Zygosity.unk,
        }
        genotype = genotype_map.get(variant_call.zygosity, self.new_model.Zygosity.unk)
        if variant_call.zygosity != genotype:
            logging.warning("Can not migrate variant call to genotype when zygosity is: {} so migrating to {}".format(
                variant_call.zygosity, self.new_model.Zygosity.unk,
            ))

        new_called_genotype = self.new_model.CalledGenotype(
            gelId=variant_call.participantId,
            sampleId=variant_call.sampleId,
            genotype=genotype,
            phaseSet=variant_call.phaseSet,
            depthReference=variant_call.depthReference,
            depthAlternate=variant_call.depthAlternate,
        )
        return self.validate_object(object_to_validate=new_called_genotype, object_type=self.new_model.CalledGenotype)

    def migrate_cancer_interpreted_genome(self, old_instance):
        new_instance = self.convert_class(self.new_model.CancerInterpretedGenome, old_instance)
        new_instance.reportedVariants = self.migrate_reported_variants_cancer(old_instance.variants)
        new_instance.reportRequestId = old_instance.interpretationRequestId
        new_instance.reportUri = old_instance.reportUrl or ""
        new_instance.analysisId = ""
        new_instance.reportedStructuralVariants = []

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.CancerInterpretedGenome
        )

    def migrate_interpretation_request_rd_plus_interpreted_genome_rd(self, old_interpretation_request, old_interpreted_genome):
        new_instance = self.convert_class(target_klass=self.new_model.InterpretationRequestRD, instance=old_interpretation_request)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        new_instance.genomeAssemblyVersion = old_interpretation_request.genomeAssembly
        new_instance.pedigree = MigrateParticipant110To100().migrate_pedigree(old_pedigree=old_interpretation_request.pedigree)
        new_instance.cellbaseVersion = ""
        new_instance.interpretGenome = False
        new_instance.tieredVariants = self.migrate_reported_variants(old_reported_variants=old_interpreted_genome.variants)
        new_instance.tieringVersion = ""
        new_instance.analysisReturnUri = ""

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD)

    def migrate_interpretation_request_cancer_plus_cancer_interpreted_genome(self, old_interpretation_request, old_interpreted_genome):
        new_instance = self.convert_class(target_klass=self.new_model.CancerInterpretationRequest, instance=old_interpretation_request)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        new_instance.reportRequestId = old_interpretation_request.interpretationRequestId
        new_instance.reportVersion = old_interpretation_request.interpretationRequestVersion
        new_instance.interpretGenome = True
        if new_instance.bams is None:
            new_instance.bams = []
        if new_instance.vcfs is None:
            new_instance.vcfs = []
        if new_instance.bigWigs is None:
            new_instance.bigWigs = []
        if old_interpretation_request.cancerParticipant:
            participant_103 = MigrateParticipant110To103().migrate_cancer_participant(
                old_participant=old_interpretation_request.cancerParticipant
            )
            new_instance.cancerParticipant = MigrationParticipants103To100().migrate_cancer_participant(
                cancer_participant=participant_103
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
        new_instance.analysisVersion = ""
        new_instance.analysisUri = ""
        new_instance.tieringVersion = ""    # TODO: can we fetch this from report events?
        new_instance.tieredVariants = self.migrate_reported_variants_cancer(old_variants=old_interpreted_genome.variants)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD)

    def migrate_reported_variants_cancer(self, old_variants):
        return [self.migrate_reported_variant_cancer_to_reported_somatic_variant(old_variant=old_variant) for old_variant in old_variants]

    def migrate_reported_variant_cancer_to_reported_somatic_variant(self, old_variant):
        """
        Migrate 5.0.0 ReportedVariantCancer to 4.0.0 ReportedSomaticVariants
        """
        new_instance = self.convert_class(target_klass=self.new_model.ReportedSomaticVariants, instance=old_variant)
        new_instance.reportedVariantCancer = self.migrate_reported_variant_cancer(old_rvc=old_variant)
        new_instance.alleleOrigins = old_variant.alleleOrigins
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ReportedSomaticVariants)

    def migrate_reported_variant_cancer(self, old_rvc):
        """
        Migrate 5.0.0 ReportedVariantCancer to 4.0.0 ReportedVariantCancer
        """
        new_instance = self.convert_class(target_klass=self.new_model.ReportedVariantCancer, instance=old_rvc)
        if old_rvc.cdnaChanges:
            new_instance.cDnaChange = next((e for e in old_rvc.cdnaChanges), None)
        if old_rvc.proteinChanges:
            new_instance.proteinChange = next((e for e in old_rvc.proteinChanges), None)
        new_instance.reportEvents = self.migrate_report_events_cancer(old_RECs=old_rvc.reportEvents)
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
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ReportedSomaticVariants)

    def migrate_report_events_cancer(self, old_RECs):
        return [self.migrate_report_event_cancer(old_rec=old_rec) for old_rec in old_RECs]

    def migrate_report_event_cancer(self, old_rec):
        new_instance = self.convert_class(target_klass=self.new_model.ReportEventCancer, instance=old_rec)
        new_instance.tier = self.tier_map.get(old_rec.tier)
        new_instance.soTerms = self.migrate_variant_consequences_to_so_terms(old_consequences=old_rec.variantConsequences)
        new_instance.genomicFeatureCancer = self.migrate_genomic_entities_to_genomic_feature_cancer(
            genomic_entities=old_rec.genomicEntities,
        )
        new_instance.actions = self.migrate_actions(old_rec.actions)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ReportEventCancer)

    def migrate_variant_consequences_to_so_terms(self, old_consequences):
        return [self.migrate_variant_consequence_to_so_term(vc=vc) for vc in old_consequences]

    def migrate_variant_consequence_to_so_term(self, vc):
        so_term = self.new_model.SoTerm(id=vc.id)
        so_term.name = vc.name if vc.name else ""
        return self.validate_object(object_to_validate=so_term, object_type=self.new_model.ReportEventCancer)

    def migrate_genomic_entities_to_genomic_feature_cancer(self, genomic_entities):
        genomic_entity = next((ge for ge in genomic_entities), self.old_model.GenomicEntity(
            type=self.old_model.GenomicEntityType.gene, ensemblId=""))
        new_instance = self.convert_class(target_klass=self.new_model.GenomicFeatureCancer, instance=genomic_entity)
        new_instance.featureType = self.migrate_genomic_entity_type_to_feature_type(old_type=genomic_entity.type)
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

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.GenomicFeatureCancer)

    def migrate_genomic_entity_type_to_feature_type(self, old_type):
        feature_type_map = {
            self.old_model.GenomicEntityType.transcript: self.new_model.FeatureTypes.Transcript,
            self.old_model.GenomicEntityType.regulatory_region: self.new_model.FeatureTypes.RegulatoryRegion,
            self.old_model.GenomicEntityType.gene: self.new_model.FeatureTypes.Gene,
        }
        if old_type not in feature_type_map.keys():
            msg = "GenomicEntityType: {ge_type} is being replaced with {rep} as an equivalent does not exist "
            msg += "in reports_4_0_0 FeatureTypes"
            logging.warning(msg=msg.format(ge_type=old_type, rep=self.new_model.FeatureTypes.Gene))
        return feature_type_map.get(old_type, self.new_model.FeatureTypes.Gene)

    def migrate_actions(self, old_actions):
        if old_actions is None:
            return None
        return [self.migrate_action(old_action=old_action) for old_action in old_actions]

    def migrate_action(self, old_action):
        new_instance = self.convert_class(target_klass=self.new_model.Actions, instance=old_action)
        new_instance.evidence = old_action.references
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Actions)

    def migrate_cancer_clinical_report(self, old_instance):
        new_instance = self.convert_class(target_klass=self.new_model.ClinicalReportCancer, instance=old_instance)
        new_instance.interpretationRequestVersion = str(old_instance.interpretationRequestVersion)
        new_instance.genePanelsCoverage = {}
        new_instance.candidateVariants = self.migrate_reported_variants_cancer(old_variants=old_instance.variants)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ClinicalReportCancer)

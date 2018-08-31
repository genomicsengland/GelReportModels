import logging

from protocols import reports_6_0_0
from protocols import reports_5_0_0
from protocols.migration.base_migration import BaseMigrateReports500And600
from protocols.reports_6_0_0 import diseaseType, TissueSource


class MigrateReports600To500(BaseMigrateReports500And600):

    old_model = reports_6_0_0
    new_model = reports_5_0_0

    moh_map = {
        old_model.ModeOfInheritance.unknown: new_model.ReportedModeOfInheritance.unknown,
        old_model.ModeOfInheritance.na: new_model.ReportedModeOfInheritance.unknown,
        old_model.ModeOfInheritance.monoallelic: new_model.ReportedModeOfInheritance.monoallelic,
        old_model.ModeOfInheritance.monoallelic_not_imprinted: new_model.ReportedModeOfInheritance.monoallelic_not_imprinted,
        old_model.ModeOfInheritance.monoallelic_maternally_imprinted: new_model.ReportedModeOfInheritance.monoallelic_maternally_imprinted,
        old_model.ModeOfInheritance.monoallelic_paternally_imprinted: new_model.ReportedModeOfInheritance.monoallelic_paternally_imprinted,
        old_model.ModeOfInheritance.biallelic: new_model.ReportedModeOfInheritance.biallelic,
        old_model.ModeOfInheritance.monoallelic_and_biallelic: new_model.ReportedModeOfInheritance.monoallelic_and_biallelic,
        old_model.ModeOfInheritance.monoallelic_and_more_severe_biallelic: new_model.ReportedModeOfInheritance.monoallelic_and_more_severe_biallelic,
        old_model.ModeOfInheritance.xlinked_biallelic: new_model.ReportedModeOfInheritance.xlinked_biallelic,
        old_model.ModeOfInheritance.xlinked_monoallelic: new_model.ReportedModeOfInheritance.xlinked_monoallelic,
        old_model.ModeOfInheritance.mitochondrial: new_model.ReportedModeOfInheritance.mitochondrial,
    }

    def migrate_interpretation_request_rd(self, old_instance):
        """
        Migrates a reports_6_0_0.InterpretationRequestRD into a reports_5_0_0.InterpretationRequestRD
        :type old_instance: reports_6_0_0.InterpretationRequestRD
        :rtype: reports_5_0_0.InterpretationRequestRD
        """
        new_instance = self.convert_class(target_klass=self.new_model.InterpretationRequestRD, instance=old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD)

    def migrate_interpreted_genome_to_interpreted_genome_rd(self, old_instance):
        """
        Migrates a reports_6_0_0.InterpretedGenome into a reports_5_0_0.InterpretedGenomeRD
        :type old_instance: reports_6_0_0.InterpretedGenome
        :rtype: reports_5_0_0.InterpretedGenomeRD
        """
        new_instance = self.convert_class(target_klass=self.new_model.InterpretedGenomeRD, instance=old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        new_instance.variants = self.convert_collection(
            old_instance.variants,
            self.migrate_small_variant_to_reported_variant,
            default=[],
            new_type=self.new_model.ReportedVariant,
            migrate_re=self.migrate_report_event)

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.InterpretedGenomeRD)

    def migrate_clinical_report_rd(self, old_instance):
        """
        Migrates a reports_6_0_0.ClinicalReport to a reports_5_0_0.ClinicalReportRD
        :type old_instance: reports_6_0_0.ClinicalReport
        :rtype: reports_5_0_0.ClinicalReportRD
        """
        new_instance = self.convert_class(target_klass=self.new_model.ClinicalReportRD, instance=old_instance)
        new_instance.variants = self.convert_collection(
            old_instance.variants,
            self.migrate_small_variant_to_reported_variant,
            default=[],
            new_type=self.new_model.ReportedVariant,
            migrate_re=self.migrate_report_event
        )
        new_instance.additionalAnalysisPanels = self.convert_collection(
            old_instance.additionalAnalysisPanels, self.migrate_additional_analysis_panel)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ClinicalReportRD)

    def migrate_exit_questionnaire_rd(self, old_instance):
        """
        Migrates a reports_6_0_0.RareDiseaseExitQuestionnaire to a reports_5_0_0.RareDiseaseExitQuestionnaire
        :type old_instance: reports_6_0_0.RareDiseaseExitQuestionnaire
        :rtype: reports_5_0_0.RareDiseaseExitQuestionnaire
        """
        new_instance = self.convert_class(
            target_klass=self.new_model.RareDiseaseExitQuestionnaire, instance=old_instance)
        new_instance.variantGroupLevelQuestions = [self.migrate_variant_group_level_questions(gq)
                                                   for gq in old_instance.variantGroupLevelQuestions]
        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.RareDiseaseExitQuestionnaire)

    def migrate_variant_group_level_questions(self, old_instance):
        new_instance = self.convert_class(target_klass=self.new_model.VariantGroupLevelQuestions, instance=old_instance)
        new_instance.variantLevelQuestions = [self.migrate_variant_level_questions(vq)
                                              for vq in old_instance.variantLevelQuestions]
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.VariantGroupLevelQuestions)

    def migrate_variant_level_questions(self, old_instance):
        new_instance = self.convert_class(target_klass=self.new_model.VariantLevelQuestions, instance=old_instance)
        coords = old_instance.variantCoordinates
        new_instance.variantDetails = "{chromosome}:{position}:{reference}:{alternate}".format(
            chromosome=coords.chromosome, position=coords.position, reference=coords.reference,
            alternate=coords.alternate)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.VariantLevelQuestions)

    def migrate_small_variant_to_reported_variant(self, small_variant, new_type, migrate_re):
        """
        Migrates a reports_6_0_0.SmallVariant into a reports_5_0_0.ReportedVariant
        :type small_variant: reports_6_0_0.SmallVariant
        :type new_type: Class
        :type migrate_re: function
        :rtype: reports_5_0_0.ReportedVariant
        """
        new_instance = self.convert_class(target_klass=new_type, instance=small_variant)

        var_attrs = small_variant.variantAttributes
        if var_attrs:
            new_instance.genomicChanges = var_attrs.genomicChanges
            new_instance.cdnaChanges = var_attrs.cdnaChanges
            new_instance.proteinChanges = var_attrs.proteinChanges
            new_instance.additionalTextualVariantAnnotations = var_attrs.additionalTextualVariantAnnotations
            new_instance.references = var_attrs.references
            new_instance.additionalNumericVariantAnnotations = var_attrs.additionalNumericVariantAnnotations
            new_instance.comments = var_attrs.comments
            new_instance.alleleOrigins = var_attrs.alleleOrigins
            if var_attrs.alleleFrequencies:
                new_instance.alleleFrequencies = [
                    self.convert_class(target_klass=self.new_model.AlleleFrequency, instance=allele_frequency)
                    for allele_frequency in var_attrs.alleleFrequencies
                ]
            if var_attrs.variantIdentifiers:
                new_instance.dbSnpId = var_attrs.variantIdentifiers.dbSnpId
                new_instance.cosmicIds = var_attrs.variantIdentifiers.cosmicIds
                new_instance.clinVarIds = var_attrs.variantIdentifiers.clinVarIds
            new_instance.variantAttributes = self.migrate_variant_attributes(old_variant_attributes=var_attrs)

        new_instance.variantCalls = self.convert_collection(small_variant.variantCalls, self.migrate_variant_call)
        new_instance.reportEvents = self.convert_collection(small_variant.reportEvents, migrate_re)

        if new_instance.alleleOrigins is None:
            new_instance.alleleOrigins = []

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ReportedVariant)

    def migrate_variant_attributes(self, old_variant_attributes):
        """
        Migrates a reports_6_0_0.VariantAttributes into a reports_5_0_0.VariantAttributes
        :type old_variant_attributes: reports_6_0_0.VariantAttributes
        :rtype: reports_5_0_0.VariantAttributes
        """
        new_instance = self.convert_class(target_klass=self.new_model.VariantAttributes, instance=old_variant_attributes)
        new_instance.fdp50 = str(old_variant_attributes.fdp50)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.VariantAttributes)

    def migrate_variant_call(self, old_call):
        """
        Migrates a reports_6_0_0.VariantCall into a reports_5_0_0.VariantCall
        :type old_call: reports_6_0_0.VariantCall
        :rtype: reports_5_0_0.VariantCall
        """
        new_instance = self.convert_class(target_klass=self.new_model.VariantCall, instance=old_call)
        if new_instance.alleleOrigins is None:
            new_instance.alleleOrigins = []
        new_instance.vaf = old_call.sampleVariantAlleleFrequency
        if old_call.phaseGenotype is not None:
            new_instance.phaseSet = old_call.phaseGenotype.phaseSet
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.VariantCall)

    def migrate_report_event(self, old_event):
        """
        Migrates a reports_6_0_0.ReportEvent into a reports_5_0_0.ReportEvent
        :type old_event: reports_6_0_0.ReportEvent
        :rtype: reports_5_0_0.ReportEvent
        """
        new_instance = self.convert_class(target_klass=self.new_model.ReportEvent, instance=old_event)
        if old_event.phenotypes.nonStandardPhenotype is None:
            new_instance.phenotypes = []
        else:
            new_instance.phenotypes = old_event.phenotypes.nonStandardPhenotype
        # v5 phenotypes is copied to v6 phenotypes.nonStandardPhenotype in the forward migration
        # https://github.com/genomicsengland/GelReportModels/blob/v7.1.2/protocols/migration/migration_reports_5_0_0_to_reports_6_0_0.py#L269
        new_instance.genePanel = self.migrate_gene_panel(old_panel=old_event.genePanel)
        new_instance.modeOfInheritance = self.migrate_mode_of_inheritance(old_moh=old_event.modeOfInheritance)
        new_instance.genomicEntities = self.convert_collection(old_event.genomicEntities, self.migrate_genomic_entity)
        if new_instance.variantClassification is not None:
            new_instance.variantClassification.drugResponseClassification = None

        if old_event.tier in (self.old_model.Tier.TIERA, self.old_model.Tier.TIERB):
            new_instance.tier = self.new_model.Tier.NONE
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ReportEvent)

    def migrate_gene_panel(self, old_panel):
        if old_panel is None:
            return None
        new_instance = self.convert_class(target_klass=self.new_model.GenePanel, instance=old_panel)
        if old_panel.panelName is None:
            new_instance.panelName = ""
        if old_panel.panelVersion is None:
            new_instance.panelVersion = ""
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.GenePanel)

    def migrate_mode_of_inheritance(self, old_moh):
        return self.moh_map.get(old_moh, self.new_model.ReportedModeOfInheritance.unknown)

    def migrate_genomic_entity(self, old_genomic_entity):
        new_instance = self.convert_class(target_klass=self.new_model.GenomicEntity, instance=old_genomic_entity)
        if old_genomic_entity.ensemblId is None:
            new_instance.ensemblId = ""
        new_instance.otherIds = self.migrate_genomic_entity_other_ids(old_ids=old_genomic_entity.otherIds)
        new_instance.type = self.migrate_genomic_entity_type(old_type=old_genomic_entity.type)

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.GenomicEntity)

    @staticmethod
    def migrate_genomic_entity_other_ids(old_ids):
        return None if old_ids is None else {old_id.source: old_id.identifier for old_id in old_ids}

    def migrate_genomic_entity_type(self, old_type):
        old = self.old_model.GenomicEntityType
        new = self.new_model.GenomicEntityType
        type_map = {
            old.regulatory_region: new.regulatory_region,
            old.gene: new.gene,
            old.transcript: new.transcript,
            old.intergenic: new.intergenic,
        }
        default = new.gene
        if old_type not in type_map.keys():
            logging.warning("Losing old genomic type: {old_type} and replacing with {default}".format(
                old_type=old_type, default=default
            ))
        return type_map.get(old_type, default)

    def migrate_interpretation_request_cancer(self, old_instance):
        """
        Migrates a reports_6_0_0.CancerInterpretationRequest into a reports_5_0_0.CancerInterpretationRequest
        :type old_instance: reports_6_0_0.CancerInterpretationRequest
        :rtype: reports_5_0_0.CancerInterpretationRequest
        """
        new_instance = self.convert_class(self.new_model.CancerInterpretationRequest, old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()

        if new_instance.cancerParticipant and new_instance.cancerParticipant.tumourSamples:
            samples = new_instance.cancerParticipant.tumourSamples
            for sample in samples:
                if sample.diseaseType in (diseaseType.ENDOCRINE, diseaseType.OTHER):
                    sample.diseaseType = None
                if sample.tissueSource == TissueSource.NOT_SPECIFIED:
                    sample.tissueSource = None

        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.CancerInterpretationRequest
        )

    def migrate_cancer_interpreted_genome(self, old_instance):
        new_instance = self.convert_class(target_klass=self.new_model.CancerInterpretedGenome, instance=old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        new_instance.variants = self.convert_collection(old_instance.variants, self.migrate_variant_cancer)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.CancerInterpretedGenome)

    def migrate_variant_cancer(self, old_variant):
        new_variant = self.convert_class(self.new_model.ReportedVariantCancer, old_variant)
        if old_variant.variantAttributes:
            attributes = old_variant.variantAttributes.toJsonDict()
            new_variant.updateWithJsonDict(attributes)
            new_variant.variantAttributes.fdp50 = str(old_variant.variantAttributes.fdp50)
            if old_variant.variantAttributes.variantIdentifiers:
                identifiers = old_variant.variantAttributes.variantIdentifiers.toJsonDict()
                new_variant.updateWithJsonDict(identifiers)

        new_variant.variantCalls = self.convert_collection(old_variant.variantCalls, self.migrate_variant_call_cancer)
        new_variant.reportEvents = self.convert_collection(old_variant.reportEvents, self.migrate_report_event_cancer)

        if new_variant.alleleOrigins is None:
            new_variant.alleleOrigins = []

        return new_variant

    def migrate_variant_call_cancer(self, old_variant_call):
        new_variant_call = self.convert_class(self.new_model.VariantCall, old_variant_call)
        if old_variant_call.phaseGenotype:
            new_variant_call.phaseSet = old_variant_call.phaseGenotype.phaseSet
        new_variant_call.vaf = old_variant_call.sampleVariantAlleleFrequency
        if new_variant_call.alleleOrigins is None:
            new_variant_call.alleleOrigins = []
        return self.validate_object(
            object_to_validate=new_variant_call, object_type=self.new_model.VariantCall
        )

    def migrate_report_event_cancer(self, old_report_event):
        new_event = self.convert_class(target_klass=self.new_model.ReportEventCancer, instance=old_report_event)
        new_event.genomicEntities = [self.migrate_genomic_entity(entity) for entity in old_report_event.genomicEntities]
        new_event.variantClassification = self.migrate_variant_classification(
            classification=old_report_event.variantClassification)

        if old_report_event.domain:
            new_event.tier = self.domain_tier_map[old_report_event.domain]
        new_event.actions = self.migrate_actions(old_report_event.actions)

        return self.validate_object(object_to_validate=new_event, object_type=self.new_model.ReportEvent)

    def migrate_variant_classification(self, classification):
        if classification is None:
            return None
        new_variant_classification = self.convert_class(self.new_model.VariantClassification, classification)
        new_variant_classification.clinicalSignificance = self.migrate_clinical_significance(
            old_significance=classification.clinicalSignificance)
        new_variant_classification.drugResponseClassification = None
        return self.validate_object(object_to_validate=new_variant_classification,
                                    object_type=self.new_model.VariantClassification)

    def migrate_clinical_significance(self, old_significance):
        return self.clinical_signicance_reverse_map.get(old_significance)

    def migrate_actions(self, actions):
        if not actions:
            return []
        evidences = [("Trial", actions.trials), ("Prognostic", actions.prognosis), ("Therapeutic", actions.therapies)]
        present_evidences = [(typ, evidence) for typ, evidence in evidences if evidence]
        return [self._make_action_from(e, typ) for typ, evidence in present_evidences for e in evidence]

    def _make_action_from(self, evidence, evidenceType):
        action = self.new_model.Action()
        action.actionType = {"Trial": "therapy", "Therapeutic": "therapeutic", "Prognostic": "prognosis"}[evidenceType]
        action.evidenceType = evidenceType
        if hasattr(evidence, 'source'):
            action.source = evidence.source
        else:
            action.source = "None"
        if hasattr(evidence, 'references'):
            action.references = evidence.references
        if hasattr(evidence, 'studyUrl'):
            action.url = evidence.studyUrl
        if hasattr(evidence, 'referenceUrl'):
            action.url = evidence.referenceUrl
        action.variantActionable = evidence.variantActionable
        action.evidenceType += ",".join([' ('] + evidence.conditions + [')'])
        return action

    def migrate_additional_analysis_panel(self, old_panel):
        new_instance = self.convert_class(target_klass=self.new_model.AdditionalAnalysisPanel, instance=old_panel)
        new_instance.panel = self.migrate_gene_panel(old_panel=old_panel.panel)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ClinicalReportRD)

    def migrate_clinical_report_cancer(self, old_instance):
        new_instance = self.convert_class(target_klass=self.new_model.ClinicalReportCancer, instance=old_instance)
        new_instance.variants = self.convert_collection(
            old_instance.variants,
            self.migrate_small_variant_to_reported_variant,
            default=[],
            new_type=self.new_model.ReportedVariantCancer,
            migrate_re=self.migrate_report_event_cancer
        )

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ClinicalReportCancer)

    def migrate_cancer_exit_questionnaire(self, old_instance):
        new_object_type = self.new_model.CancerExitQuestionnaire
        new_instance = self.convert_class(target_klass=new_object_type, instance=old_instance)
        new_instance.somaticVariantLevelQuestions = self.convert_collection(
            things=old_instance.somaticVariantLevelQuestions,
            migrate_function=self.migrate_only_variant_details,
            klass=self.new_model.CancerSomaticVariantLevelQuestions
        )
        new_instance.germlineVariantLevelQuestions = self.convert_collection(
            things=old_instance.germlineVariantLevelQuestions,
            migrate_function=self.migrate_only_variant_details,
            klass=self.new_model.CancerGermlineVariantLevelQuestions
        )
        new_instance.otherActionableVariants = self.convert_collection(
            things=old_instance.otherActionableVariants,
            migrate_function=self.migrate_only_variant_details,
            klass=self.new_model.AdditionalVariantsQuestions
        )
        return self.validate_object(object_to_validate=new_instance, object_type=new_object_type)

    def migrate_only_variant_details(self, old_instance, klass):
        new_instance = self.convert_class(target_klass=klass, instance=old_instance)
        new_instance.variantDetails = self.migrate_variant_coordinates_to_variant_details(
            old_coordinates=old_instance.variantCoordinates)
        return self.validate_object(object_to_validate=new_instance, object_type=klass)

    @staticmethod
    def migrate_variant_coordinates_to_variant_details(old_coordinates):
        variant_details_template = "{chromosome}:{position}:{reference}:{alternate}"
        return variant_details_template.format(
            chromosome=old_coordinates.chromosome,
            position=old_coordinates.position,
            reference=old_coordinates.reference,
            alternate=old_coordinates.alternate,
        )

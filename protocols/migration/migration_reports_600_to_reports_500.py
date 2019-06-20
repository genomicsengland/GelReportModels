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
        if old_instance.variants is not None:
            new_instance.variants = self.convert_collection(
                list(zip(old_instance.variants, new_instance.variants)),
                self._migrate_variant,
                default=[],
                migrate_re=self._migrate_report_event)
        else:
            new_instance.variants = []

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.InterpretedGenomeRD)

    def migrate_clinical_report_rd(self, old_instance):
        """
        Migrates a reports_6_0_0.ClinicalReport to a reports_5_0_0.ClinicalReportRD
        :type old_instance: reports_6_0_0.ClinicalReport
        :rtype: reports_5_0_0.ClinicalReportRD
        """
        new_instance = self.convert_class(target_klass=self.new_model.ClinicalReportRD, instance=old_instance)
        if old_instance.variants is not None:
            new_instance.variants = self.convert_collection(
                list(zip(old_instance.variants, new_instance.variants)),
                self._migrate_variant,
                default=[],
                migrate_re=self._migrate_report_event
            )
        else:
            new_instance.variants = []
        new_instance.additionalAnalysisPanels = self.convert_collection(
            old_instance.additionalAnalysisPanels, self._migrate_additional_analysis_panel)
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
        new_instance.variantGroupLevelQuestions = [self._migrate_variant_group_level_questions(gq)
                                                   for gq in old_instance.variantGroupLevelQuestions]
        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.RareDiseaseExitQuestionnaire)

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
        """
        :type old_instance: reports_6_0_0.InterpretedGenome
        :rtype: reports_5_0_0.CancerInterpretedGenome
        """
        new_instance = self.convert_class(target_klass=self.new_model.CancerInterpretedGenome, instance=old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        if old_instance.variants:
            new_instance.variants = self.convert_collection(
                list(zip(old_instance.variants, new_instance.variants)),
                self._migrate_variant,
                migrate_re=self._migrate_report_event_cancer)
        else:
            new_instance.variants = []
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.CancerInterpretedGenome)

    def migrate_clinical_report_cancer(self, old_instance):
        """
        :type old_instance: reports_6_0_0.ClinicalReport
        :rtype: reports_5_0_0.ClinicalReportCancer
        """
        new_instance = self.convert_class(target_klass=self.new_model.ClinicalReportCancer, instance=old_instance)
        if old_instance.variants is not None:
            new_instance.variants = self.convert_collection(
                list(zip(old_instance.variants, new_instance.variants)),
                self._migrate_variant,
                default=[],
                migrate_re=self._migrate_report_event_cancer
            )
        else:
            new_instance.variants = []

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ClinicalReportCancer)

    def migrate_cancer_exit_questionnaire(self, old_instance):
        """
        :type old_instance: reports_6_0_0.CancerExitQuestionnaire
        :rtype: reports_5_0_0.CancerExitQuestionnaire
        """
        new_object_type = self.new_model.CancerExitQuestionnaire
        new_instance = self.convert_class(target_klass=new_object_type, instance=old_instance)
        new_instance.somaticVariantLevelQuestions = self.convert_collection(
            things=old_instance.somaticVariantLevelQuestions,
            migrate_function=self._migrate_only_variant_details,
            klass=self.new_model.CancerSomaticVariantLevelQuestions
        )
        new_instance.germlineVariantLevelQuestions = self.convert_collection(
            things=old_instance.germlineVariantLevelQuestions,
            migrate_function=self._migrate_only_variant_details,
            klass=self.new_model.CancerGermlineVariantLevelQuestions
        )
        new_instance.otherActionableVariants = self.convert_collection(
            things=old_instance.otherActionableVariants,
            migrate_function=self._migrate_only_variant_details,
            klass=self.new_model.AdditionalVariantsQuestions
        )
        return self.validate_object(object_to_validate=new_instance, object_type=new_object_type)

    def _migrate_variant_group_level_questions(self, old_instance):
        new_instance = self.convert_class(target_klass=self.new_model.VariantGroupLevelQuestions, instance=old_instance)
        new_instance.variantLevelQuestions = [self._migrate_variant_level_questions(vq)
                                              for vq in old_instance.variantLevelQuestions]
        return new_instance

    def _migrate_variant_level_questions(self, old_instance):
        new_instance = self.convert_class(target_klass=self.new_model.VariantLevelQuestions, instance=old_instance)
        coords = old_instance.variantCoordinates
        new_instance.variantDetails = "{chromosome}:{position}:{reference}:{alternate}".format(
            chromosome=coords.chromosome, position=coords.position, reference=coords.reference,
            alternate=coords.alternate)
        return new_instance

    def _migrate_variant_attributes(self, old_variant_attributes):
        new_instance = self.convert_class(target_klass=self.new_model.VariantAttributes, instance=old_variant_attributes)
        new_instance.fdp50 = str(old_variant_attributes.fdp50)
        return new_instance

    def _migrate_variant_call(self, variant_calls):
        old_instance = variant_calls[0]
        new_instance = variant_calls[1]
        if new_instance.alleleOrigins is None:
            new_instance.alleleOrigins = []
        new_instance.vaf = old_instance.sampleVariantAlleleFrequency
        if old_instance.phaseGenotype is not None:
            new_instance.phaseSet = old_instance.phaseGenotype.phaseSet
        return new_instance

    def _migrate_report_event(self, report_events):
        old_instance = report_events[0]
        new_instance = report_events[1]
        if old_instance.phenotypes.nonStandardPhenotype is None:
            new_instance.phenotypes = []
        else:
            new_instance.phenotypes = old_instance.phenotypes.nonStandardPhenotype
        # v5 phenotypes is copied to v6 phenotypes.nonStandardPhenotype in the forward migration
        # https://github.com/genomicsengland/GelReportModels/blob/v7.1.2/protocols/migration/migration_reports_5_0_0_to_reports_6_0_0.py#L269
        new_instance.genePanel = self._migrate_gene_panel((old_instance.genePanel, new_instance.genePanel))
        new_instance.modeOfInheritance = self._migrate_mode_of_inheritance(old_moh=old_instance.modeOfInheritance)
        new_instance.genomicEntities = self.convert_collection(
            list(zip(old_instance.genomicEntities, new_instance.genomicEntities)), self._migrate_genomic_entity)
        if old_instance.segregationPattern is not None and new_instance.eventJustification is None:
            new_instance.eventJustification = "passed the {} segregation filter".format(old_instance.segregationPattern)
        if new_instance.variantClassification is not None:
            new_instance.variantClassification.drugResponseClassification = None

        if old_instance.tier in (self.old_model.Tier.TIERA, self.old_model.Tier.TIERB):
            new_instance.tier = self.new_model.Tier.NONE
        return new_instance

    def _migrate_report_event_cancer(self, report_events):
        old_instance = report_events[0]
        new_instance = report_events[1]
        new_instance.genomicEntities = self.convert_collection(
            list(zip(old_instance.genomicEntities, new_instance.genomicEntities)), self._migrate_genomic_entity)
        new_instance.variantClassification = self._migrate_variant_classification(
            classification=old_instance.variantClassification)
        if old_instance.domain:
            new_instance.tier = self.domain_tier_map[old_instance.domain]
        new_instance.actions = self._migrate_actions(old_instance.actions)
        if old_instance.tier in (self.old_model.Tier.TIERA, self.old_model.Tier.TIERB):
            new_instance.tier = self.new_model.Tier.NONE
        return new_instance

    def _migrate_gene_panel(self, gene_panels):
        old_instance = gene_panels[0]
        new_instance = gene_panels[1]
        if old_instance is None:
            return None
        if old_instance.panelName is None:
            new_instance.panelName = ""
        if old_instance.panelVersion is None:
            new_instance.panelVersion = ""
        return new_instance

    def _migrate_mode_of_inheritance(self, old_moh):
        return self.moh_map.get(old_moh, self.new_model.ReportedModeOfInheritance.unknown)

    def _migrate_genomic_entity(self, genomic_entities):
        old_instance = genomic_entities[0]
        new_instance = genomic_entities[1]
        if old_instance.ensemblId is None:
            new_instance.ensemblId = ""
        new_instance.otherIds = self._migrate_genomic_entity_other_ids(old_ids=old_instance.otherIds)
        new_instance.type = self._migrate_genomic_entity_type(old_type=old_instance.type)
        return new_instance

    @staticmethod
    def _migrate_genomic_entity_other_ids(old_ids):
        return None if old_ids is None else {old_id.source: old_id.identifier for old_id in old_ids}

    def _migrate_genomic_entity_type(self, old_type):
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

    def _migrate_variant(self, variants, migrate_re):

        old_instance = variants[0]
        new_instance = variants[1]

        if old_instance.variantAttributes:
            attributes = old_instance.variantAttributes.toJsonDict()
            new_instance.updateWithJsonDict(attributes)
            new_instance.variantAttributes.fdp50 = str(old_instance.variantAttributes.fdp50)
            if old_instance.variantAttributes.variantIdentifiers:
                identifiers = old_instance.variantAttributes.variantIdentifiers.toJsonDict()
                new_instance.updateWithJsonDict(identifiers)
            if old_instance.variantAttributes.alleleFrequencies:
                new_instance.alleleFrequencies = [
                    self.convert_class(target_klass=self.new_model.AlleleFrequency, instance=allele_frequency)
                    for allele_frequency in old_instance.variantAttributes.alleleFrequencies
                ]
        new_instance.variantCalls = self.convert_collection(
            list(zip(old_instance.variantCalls, new_instance.variantCalls)), self._migrate_variant_call)
        new_instance.reportEvents = self.convert_collection(
            list(zip(old_instance.reportEvents, new_instance.reportEvents)), migrate_re)

        if new_instance.alleleOrigins is None:
            new_instance.alleleOrigins = []

        return new_instance

    def _migrate_variant_classification(self, classification):
        if classification is None:
            return None
        new_variant_classification = self.convert_class(self.new_model.VariantClassification, classification)
        new_variant_classification.clinicalSignificance = self._migrate_clinical_significance(
            old_significance=classification.clinicalSignificance)
        new_variant_classification.drugResponseClassification = None
        return new_variant_classification

    def _migrate_clinical_significance(self, old_significance):
        return self.clinical_signicance_reverse_map.get(old_significance)

    def _migrate_actions(self, actions):
        if not actions:
            return []
        evidences = [("Trial", actions.trials), ("Prognostic", actions.prognosis), ("Therapeutic", actions.therapies)]
        present_evidences = [(typ, evidence) for typ, evidence in evidences if evidence]
        return [self._make_action_from(e, typ) for typ, evidence in present_evidences for e in evidence]

    def _make_action_from(self, evidence, evidence_type):
        action = self.new_model.Action()
        action.evidenceType = "{} ({})".format(evidence_type, ", ".join(evidence.conditions))
        action.actionType = None
        if hasattr(evidence, 'source') and evidence.source is not None:
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
        return action

    def _migrate_additional_analysis_panel(self, old_panel):
        new_instance = self.convert_class(target_klass=self.new_model.AdditionalAnalysisPanel, instance=old_panel)
        new_instance.panel = self._migrate_gene_panel((old_panel.panel, new_instance.panel))
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.ClinicalReportRD)

    def _migrate_only_variant_details(self, old_instance, klass):
        new_instance = self.convert_class(target_klass=klass, instance=old_instance)
        new_instance.variantDetails = self._migrate_variant_coordinates_to_variant_details(
            old_coordinates=old_instance.variantCoordinates)
        return self.validate_object(object_to_validate=new_instance, object_type=klass)

    @staticmethod
    def _migrate_variant_coordinates_to_variant_details(old_coordinates):
        variant_details_template = "{chromosome}:{position}:{reference}:{alternate}"
        return variant_details_template.format(
            chromosome=old_coordinates.chromosome,
            position=old_coordinates.position,
            reference=old_coordinates.reference,
            alternate=old_coordinates.alternate,
        )

import logging

from protocols import reports_6_0_0
from protocols import reports_5_0_0
from protocols.migration.base_migration import (
    BaseMigration,
    MigrationError,
)
import re


class MigrateReports500To600(BaseMigration):

    old_model = reports_5_0_0
    new_model = reports_6_0_0

    def migrate_interpretation_request_rd(self, old_instance):
        """
        Migrates a reports_5_0_0.InterpretationRequestRD into a reports_6_0_0.InterpretationRequestRD
        :type old_instance: reports_5_0_0.InterpretationRequestRD
        :rtype: reports_6_0_0.InterpretationRequestRD
        """
        new_instance = self.convert_class(self.new_model.InterpretationRequestRD, old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD
        )

    def migrate_interpretation_request_cancer(self, old_instance):
        """
        Migrates a reports_5_0_0.CancerInterpretationRequest into a reports_6_0_0.CancerInterpretationRequest
        :type old_instance: reports_5_0_0.CancerInterpretationRequest
        :rtype: reports_6_0_0.CancerInterpretationRequest
        """
        new_instance = self.convert_class(self.new_model.CancerInterpretationRequest, old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD
        )

    def migrate_interpreted_genome_rd(self, old_instance, panel_source='panelapp'):
        """
        Migrates a reports_5_0_0.InterpretedGenomeRD into a reports_6_0_0.InterpretedGenome
        :type old_instance: reports_5_0_0.InterpretedGenomeRD
        :type panel_source: str
        :rtype: reports_6_0_0.InterpretedGenome
        """
        new_instance = self.convert_class(self.new_model.InterpretedGenome, old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        new_instance.variants = self.migrate_variants(old_variants=old_instance.variants, panel_source=panel_source)
        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretedGenome
        )

    def migrate_variants(self, old_variants, panel_source='panelapp'):
        if old_variants is None:
            return None
        return [self.migrate_variant(old_variant=old_variant, panel_source=panel_source) for old_variant in old_variants]

    def migrate_variant(self, old_variant, panel_source='panelapp'):
        """
        Migrates a reports_5_0_0.ReportedVariant to a reports_6_0_0.SmallVariant
        :type old_variant: reports_5_0_0.ReportedVariant
        :type panel_source: str
        :rtype: reports_6_0_0.SmallVariant
        """

        new_variant = self.convert_class(self.new_model.SmallVariant, old_variant)
        new_variant.variantCalls = self.migrate_variant_calls(variant_calls=old_variant.variantCalls)
        new_variant.reportEvents = self.migrate_report_events(report_events=old_variant.reportEvents, panel_source=panel_source)
        new_variant.variantAttributes = self.migrate_variant_attributes(old_variant=old_variant)
        return self.validate_object(
            object_to_validate=new_variant, object_type=self.new_model.SmallVariant
        )

    def migrate_variant_attributes(self, old_variant):
        # This logic is done here because alleleOrigins is part of the
        # v6 variantAttributes, which is non-nullable in v5 (or v6)
        # so the v5 variantAttributes could be null, but the alleleOrigins can not be,
        # so this is done to make sure we don't lose the alleleOrigins
        if old_variant.variantAttributes is not None:
            new_variant_attributes = self.convert_class(self.new_model.VariantAttributes, old_variant.variantAttributes)
            if old_variant.variantAttributes.fdp50 is not None:
                new_variant_attributes.fdp50 = self.migrate_fdp50(fdp50=old_variant.variantAttributes.fdp50)
        else:
            new_variant_attributes = self.new_model.VariantAttributes()

        new_variant_attributes.genomicChanges = old_variant.genomicChanges
        new_variant_attributes.cdnaChanges = old_variant.cdnaChanges
        new_variant_attributes.proteinChanges = old_variant.proteinChanges
        new_variant_attributes.additionalTextualVariantAnnotations = old_variant.additionalTextualVariantAnnotations
        new_variant_attributes.references = old_variant.references
        new_variant_attributes.additionalNumericVariantAnnotations = old_variant.additionalNumericVariantAnnotations
        new_variant_attributes.comments = old_variant.comments
        new_variant_attributes.alleleOrigins = old_variant.alleleOrigins
        new_variant_attributes.alleleFrequencies = self.migrate_allele_frequencies(old_frequencies=old_variant.alleleFrequencies)
        variant_identifiers = self.new_model.VariantIdentifiers(
            dbSnpId=old_variant.dbSnpId,
            cosmicIds=old_variant.cosmicIds,
            clinVarIds=old_variant.clinVarIds,
        )
        variant_identifiers = self.validate_object(object_to_validate=variant_identifiers, object_type=self.new_model.VariantIdentifiers)
        new_variant_attributes.variantIdentifiers = variant_identifiers
        return self.validate_object(object_to_validate=new_variant_attributes, object_type=self.new_model.VariantAttributes)

    @staticmethod
    def migrate_fdp50(fdp50):
        try:
            return float(fdp50)
        except ValueError:
            logging.warning("Losing fdp50 value: {fdp50} as it can not be converted to a float".format(fdp50=fdp50))
            return None

    def migrate_allele_frequencies(self, old_frequencies):
        if old_frequencies is None:
            return None
        return [self.migrate_allele_frequency(old_frequency=old_frequency) for old_frequency in old_frequencies]

    def migrate_allele_frequency(self, old_frequency):
        new_frequency = self.convert_class(self.new_model.AlleleFrequency, old_frequency)
        return self.validate_object(object_to_validate=new_frequency, object_type=self.new_model.AlleleFrequency)

    def migrate_variant_calls(self, variant_calls):
        return [self.migrate_variant_call(variant_call=variant_call) for variant_call in variant_calls]

    def migrate_variant_call(self, variant_call):
        new_variant_call = self.convert_class(self.new_model.VariantCall, variant_call)
        if variant_call.phaseSet:
            new_variant_call.phaseGenotype = self.new_model.PhaseGenotype()
            new_variant_call.phaseGenotype.phaseSet = variant_call.phaseSet
            # TODO: build this list or change the model or ...?
            new_variant_call.phaseGenotype.sortedAlleles = []
        new_variant_call.sampleVariantAlleleFrequency = variant_call.vaf
        return self.validate_object(
            object_to_validate=new_variant_call, object_type=self.new_model.VariantCall
        )

    def migrate_report_events(self, report_events, panel_source='panelapp'):
        return [self.migrate_report_event(report_event=report_event, panel_source=panel_source) for report_event in report_events]

    def migrate_report_event(self, report_event, panel_source='panelapp'):
        new_report_event = self.convert_class(self.new_model.ReportEvent, report_event)
        new_report_event.phenotypes = self.migrate_phenotypes(phenotypes=report_event.phenotypes)
        new_report_event.genePanel = self.migrate_gene_panel(gene_panel=report_event.genePanel, panel_source=panel_source)
        new_report_event.genomicEntities = self.migrate_genomic_entities(genomic_entities=report_event.genomicEntities)
        new_report_event.variantClassification = self.migrate_variant_classification(classification=report_event.variantClassification)
        if report_event.eventJustification:
            new_report_event.segregationPattern = self.migrate_segregation_pattern(event_justification=report_event.eventJustification)
        return self.validate_object(object_to_validate=new_report_event, object_type=self.new_model.ReportEvent)

    def migrate_segregation_pattern(self, event_justification):
        if re.search(self.new_model.SegregationPattern.UniparentalIsodisomy, event_justification):
            return self.new_model.SegregationPattern.UniparentalIsodisomy
        if re.search(self.new_model.SegregationPattern.SimpleRecessive, event_justification):
            return self.new_model.SegregationPattern.SimpleRecessive
        if re.search(self.new_model.SegregationPattern.CompoundHeterozygous, event_justification):
            return self.new_model.SegregationPattern.CompoundHeterozygous
        if re.search(self.new_model.SegregationPattern.deNovo, event_justification):
            return self.new_model.SegregationPattern.deNovo
        if re.search(self.new_model.SegregationPattern.InheritedAutosomalDominant, event_justification):
            return self.new_model.SegregationPattern.InheritedAutosomalDominant
        if re.search(self.new_model.SegregationPattern.InheritedAutosomalDominantMaternallyImprinted, event_justification):
            return self.new_model.SegregationPattern.InheritedAutosomalDominantMaternallyImprinted
        if re.search(self.new_model.SegregationPattern.InheritedAutosomalDominantPaternallyImprinted, event_justification):
            return self.new_model.SegregationPattern.InheritedAutosomalDominantPaternallyImprinted
        if re.search(self.new_model.SegregationPattern.XLinkedCompoundHeterozygous, event_justification):
            return self.new_model.SegregationPattern.XLinkedCompoundHeterozygous
        if re.search(self.new_model.SegregationPattern.XLinkedSimpleRecessive, event_justification):
            return self.new_model.SegregationPattern.XLinkedSimpleRecessive
        if re.search(self.new_model.SegregationPattern.XLinkedMonoallelic, event_justification):
            return self.new_model.SegregationPattern.XLinkedMonoallelic
        if re.search(self.new_model.SegregationPattern.MitochondrialGenome, event_justification):
            return self.new_model.SegregationPattern.MitochondrialGenome
        return None

    def migrate_gene_panel(self, gene_panel, panel_source='panelapp'):
        if gene_panel is None:
            return None
        new_gene_panel = self.convert_class(self.new_model.GenePanel, gene_panel)
        new_gene_panel.source = panel_source
        return self.validate_object(object_to_validate=new_gene_panel, object_type=self.new_model.GenePanel)

    def migrate_variant_classification(self, classification):
        if classification is None:
            return None
        new_variant_classification = self.convert_class(self.new_model.VariantClassification, classification)
        new_variant_classification.clinicalSignificance = self.migrate_clinical_significance(
            old_significance=classification.clinicalSignificance)
        new_variant_classification.drugResponseClassification = None
        return self.validate_object(object_to_validate=new_variant_classification, object_type=self.new_model.VariantClassification)

    def migrate_clinical_significance(self, old_significance):
        clinical_signicance_map = {
            self.old_model.ClinicalSignificance.benign: self.new_model.ClinicalSignificance.benign,
            self.old_model.ClinicalSignificance.likely_benign: self.new_model.ClinicalSignificance.likely_benign,
            self.old_model.ClinicalSignificance.pathogenic: self.new_model.ClinicalSignificance.pathogenic,
            self.old_model.ClinicalSignificance.likely_pathogenic: self.new_model.ClinicalSignificance.likely_pathogenic,
            self.old_model.ClinicalSignificance.uncertain_significance: self.new_model.ClinicalSignificance.uncertain_significance,
            self.old_model.ClinicalSignificance.VUS: self.new_model.ClinicalSignificance.uncertain_significance,
        }
        return clinical_signicance_map.get(old_significance)

    def migrate_phenotypes(self, phenotypes):
        new_phenotype = self.new_model.Phenotypes(
            nonStandardPhenotype=phenotypes,
        )
        return self.validate_object(
            object_to_validate=new_phenotype, object_type=self.new_model.Phenotypes
        )

    def migrate_genomic_entities(self, genomic_entities):
        return [self.migrate_genomic_entity(genomic_entity=genomic_entity) for genomic_entity in genomic_entities]

    def migrate_genomic_entity(self, genomic_entity):
        new_genomic_entity = self.convert_class(self.new_model.GenomicEntity, genomic_entity)
        if genomic_entity.otherIds is not None and isinstance(genomic_entity.otherIds, dict):
            new_genomic_entity.otherIds = self.migrate_other_ids(other_ids=genomic_entity.otherIds)
        return self.validate_object(
            object_to_validate=new_genomic_entity, object_type=self.new_model.GenomicEntity,
        )

    def migrate_other_ids(self, other_ids):
        return [self.migrate_other_id(source=key, identifier=value) for key, value in other_ids.items()]

    def migrate_other_id(self, source, identifier):
        identifier = self.new_model.Identifier(
            source=source,
            identifier=identifier
        )
        return self.validate_object(
            object_to_validate=identifier, object_type=self.new_model.Identifier,
        )

    def migrate_clinical_report_rd(self, old_instance):
        migrated_instance = self.convert_class(self.new_model.ClinicalReport, old_instance)
        migrated_instance.variants = self.migrate_variants(old_variants=old_instance.variants)
        return self.validate_object(object_to_validate=migrated_instance, object_type=self.new_model.ClinicalReport)

    def migrate_rd_exit_questionnaire(self, old_instance, assembly):
        migrated_instance = self.convert_class(self.new_model.RareDiseaseExitQuestionnaire, old_instance)
        migrated_instance.variantGroupLevelQuestions = self.migrate_variant_group_level_questions(
            VGLQs=old_instance.variantGroupLevelQuestions, assembly=assembly
        )
        return self.validate_object(object_to_validate=migrated_instance, object_type=self.new_model.RareDiseaseExitQuestionnaire)

    def migrate_variant_group_level_questions(self, VGLQs, assembly):
        return [self.migrate_variant_group_level_question(VGLQ=VGLQ, assembly=assembly) for VGLQ in VGLQs]

    def migrate_variant_group_level_question(self, VGLQ, assembly):
        migrated_vglq = self.convert_class(target_klass=self.new_model.VariantGroupLevelQuestions, instance=VGLQ)
        migrated_vglq.variantLevelQuestions = self.migrate_variant_level_questions(
            VLQs=VGLQ.variantLevelQuestions, assembly=assembly
        )

        return self.validate_object(object_to_validate=migrated_vglq, object_type=self.new_model.VariantGroupLevelQuestions)

    def migrate_variant_level_questions(self, VLQs, assembly):
        return [self.migrate_variant_level_question(VLQ=VLQ, assembly=assembly) for VLQ in VLQs]

    def migrate_variant_level_question(self, VLQ, assembly):
        migrated_vlq = self.convert_class(target_klass=self.new_model.VariantLevelQuestions, instance=VLQ)

        migrated_vlq.variantCoordinates = self.migrate_variant_coordinates(
            variant_details=VLQ.variantDetails, assembly=assembly
        )

        return self.validate_object(object_to_validate=migrated_vlq, object_type=self.new_model.VariantLevelQuestions)

    def migrate_variant_coordinates(self, variant_details, assembly):

        details = self.extract_variant_details(variant_details=variant_details)
        variant_coordinates = self.new_model.VariantCoordinates(
            chromosome=details.get("chromosome"),
            position=details.get("position"),
            reference=details.get("reference"),
            alternate=details.get("alternate"),
            assembly=assembly,
        )
        return self.validate_object(object_to_validate=variant_coordinates, object_type=self.new_model.VariantCoordinates)

    @staticmethod
    def extract_variant_details(variant_details):
        """
        The format of variant_details is "chr:pos:ref:alt"
        """
        details = variant_details.split(":")
        if len(details) != 4:
            raise MigrationError("Variant details: {variant_details} should be in format chr:pos:ref:alt".format(
                variant_details=variant_details
            ))
        try:
            details[1] = int(details[1])
        except ValueError:
            raise MigrationError("Position {position} is not an integer !".format(
                position=details[1]
            ))
        return {
            "chromosome": details[0],
            "position": details[1],
            "reference": details[2],
            "alternate": details[3],
        }

    def migrate_cancer_interpreted_genome(self, old_instance):
        new_instance = self.convert_class(target_klass=self.new_model.InterpretedGenome, instance=old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        new_instance.variants = self.migrate_variants_cancer(variants=old_instance.variants)

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.InterpretedGenome)

    def migrate_variants_cancer(self, variants):
        if variants is None:
            return None
        return [self.migrate_variant_cancer(variant=variant) for variant in variants]

    def migrate_variant_cancer(self, variant):
        new_variant = self.convert_class(target_klass=self.new_model.SmallVariant, instance=variant)
        new_variant.variantCalls = self.migrate_variant_calls(variant_calls=variant.variantCalls)
        new_variant.reportEvents = self.migrate_report_events_cancer(events=variant.reportEvents)
        new_variant.variantAttributes = self.migrate_variant_attributes(old_variant=variant)

        return self.validate_object(object_to_validate=new_variant, object_type=self.new_model.SmallVariant)

    def migrate_report_events_cancer(self, events):
        return [self.migrate_report_event_cancer(event=event) for event in events]

    def migrate_report_event_cancer(self, event):
        new_event = self.convert_class(target_klass=self.new_model.ReportEvent, instance=event)

        new_event.modeOfInheritance = self.new_model.ModeOfInheritance.na
        new_event.phenotypes = self.new_model.Phenotypes()
        new_event.genomicEntities = self.migrate_genomic_entities(genomic_entities=event.genomicEntities)
        new_event.variantClassification = self.migrate_variant_classification(
            classification=event.variantClassification)
        # migrate tier to domain
        new_event.tier = None
        tier_domain_map = {
            self.old_model.Tier.TIER1: self.new_model.Domain.DOMAIN1,
            self.old_model.Tier.TIER2: self.new_model.Domain.DOMAIN2,
            self.old_model.Tier.TIER3: self.new_model.Domain.DOMAIN3,
            self.old_model.Tier.TIER4: self.new_model.Domain.DOMAIN4,
            self.old_model.Tier.TIER5: self.new_model.Domain.NONE,
            self.old_model.Tier.NONE: self.new_model.Domain.NONE
        }
        if event.tier:
            new_event.domain = tier_domain_map[event.tier]
        if event.actions:
            new_event.actions = self.migrate_actions(event.actions)
        return self.validate_object(object_to_validate=new_event, object_type=self.new_model.ReportEvent)

    def migrate_actions(self, actions):

        def extract_evidence_type(evidence_type):
            # conditions are extracted from the text between brackets in evidence type
            return map(lambda x: x.strip(), re.search(".*\((.*)\)", evidence_type).group(1).split(','))

        new_actions = self.new_model.Actions()
        for action in actions:
            # map to either entity by the content of field evidence type
            if "Trial" in action.evidenceType:
                if action.url:  # NOTE: we need the url to extract the study identifier
                    trial = self.new_model.Trial()
                    trial.studyUrl = action.url
                    # extract id of study from the last component of URL
                    trial.studyIdentifier = action.url.strip('/').split('/')[-1]
                    trial.variantActionable = action.variantActionable
                    trial.conditions = extract_evidence_type(action.evidenceType)
                    if not new_actions.trials:
                        new_actions.trials = []
                    new_actions.trials.append(trial)
            elif "Prognostic" in action.evidenceType:
                prognosis = self.new_model.Prognosis()
                prognosis.referenceUrl = action.url
                prognosis.variantActionable = action.variantActionable
                prognosis.conditions = extract_evidence_type(action.evidenceType)
                if not new_actions.prognosis:
                    new_actions.prognosis = []
                new_actions.prognosis.append(prognosis)
            elif "Therapeutic" in action.evidenceType:
                therapy = self.new_model.Therapy()
                therapy.referenceUrl = action.url
                therapy.variantActionable = action.variantActionable
                therapy.conditions = extract_evidence_type(action.evidenceType)
                if not new_actions.therapies:
                    new_actions.therapies = []
                new_actions.therapies.append(therapy)
        return new_actions

    def migrate_cancer_clinical_report(self, old_instance):
        new_ccr = self.convert_class(target_klass=self.new_model.ClinicalReport, instance=old_instance)
        new_ccr.variants = self.migrate_variants_cancer(variants=old_instance.variants)
        return self.validate_object(object_to_validate=new_ccr, object_type=self.new_model.ClinicalReport)

    def migrate_cancer_exit_questionnaire(self, old_instance, assembly):
        new_c_eq = self.convert_class(target_klass=self.new_model.CancerExitQuestionnaire, instance=old_instance)
        new_c_eq.somaticVariantLevelQuestions = self.migrate_somatic_variant_level_questions(
            old_questions=old_instance.somaticVariantLevelQuestions, assembly=assembly
        )
        new_c_eq.germlineVariantLevelQuestions = self.migrate_germline_variant_level_questions(
            old_questions=old_instance.germlineVariantLevelQuestions, assembly=assembly
        )
        new_c_eq.otherActionableVariants = self.migrate_other_actionable_variants(
            old_variants=old_instance.otherActionableVariants, assembly=assembly
        )
        return self.validate_object(object_to_validate=new_c_eq, object_type=self.new_model.CancerExitQuestionnaire)

    def migrate_other_actionable_variants(self, old_variants, assembly):
        if old_variants is None:
            return None
        return [self.migrate_other_actionable_variant(old_variant=old_variant, assembly=assembly) for old_variant in old_variants]

    def migrate_somatic_variant_level_questions(self, old_questions, assembly):
        if old_questions is None:
            return None
        return [self.migrate_somatic_variant_level_question(question=question, assembly=assembly) for question in old_questions]

    def migrate_germline_variant_level_questions(self, old_questions, assembly):
        if old_questions is None:
            return None
        return [self.migrate_germline_variant_level_question(question=question, assembly=assembly) for question in old_questions]

    def migrate_somatic_variant_level_question(self, question, assembly):
        new_question = self.convert_class(target_klass=self.new_model.CancerSomaticVariantLevelQuestions, instance=question)
        new_question.variantCoordinates = self.migrate_variant_coordinates(
            variant_details=question.variantDetails, assembly=assembly
        )
        return self.validate_object(object_to_validate=new_question, object_type=self.new_model.CancerSomaticVariantLevelQuestions)

    def migrate_germline_variant_level_question(self, question, assembly):
        new_question = self.convert_class(target_klass=self.new_model.CancerGermlineVariantLevelQuestions, instance=question)
        new_question.variantCoordinates = self.migrate_variant_coordinates(
            variant_details=question.variantDetails, assembly=assembly
        )
        return self.validate_object(object_to_validate=new_question, object_type=self.new_model.CancerGermlineVariantLevelQuestions)

    def migrate_other_actionable_variant(self, old_variant, assembly):
        new_question = self.convert_class(target_klass=self.new_model.AdditionalVariantsQuestions, instance=old_variant)
        new_question.variantCoordinates = self.migrate_variant_coordinates(
            variant_details=old_variant.variantDetails, assembly=assembly
        )
        return self.validate_object(object_to_validate=new_question, object_type=self.new_model.AdditionalVariantsQuestions)

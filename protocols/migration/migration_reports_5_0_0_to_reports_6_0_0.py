import logging

from protocols import reports_6_0_0
from protocols import reports_5_0_0
from protocols import opencb_1_3_0
from protocols.migration.base_migration import (
    BaseMigration,
    MigrationError,
)
import itertools


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
        :param old_variant: reports_5_0_0.ReportedVariant
        :return: reports_6_0_0.SmallVariant
        """

        new_variant = self.convert_class(self.new_model.SmallVariant, old_variant)
        new_variant.variantCoordinates = self.convert_class(self.new_model.VariantCoordinates, old_variant.variantCoordinates)
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

        return self.validate_object(
            object_to_validate=new_variant_call, object_type=self.new_model.VariantCall
        )

    def migrate_report_events(self, report_events, panel_source='panelapp'):
        return [self.migrate_report_event(report_event=report_event, panel_source=panel_source) for report_event in report_events]

    def migrate_report_event(self, report_event, panel_source='panelapp'):
        new_report_event = self.convert_class(self.new_model.ReportEvent, report_event)
        new_report_event.phenotypes = self.migrate_phenotypes(phenotypes=report_event.phenotypes)
        new_report_event.variantConsequences = self.migrate_variant_conseuqences(variant_consequences=report_event.variantConsequences)
        new_report_event.genePanel = self.migrate_gene_panel(gene_panel=report_event.genePanel, panel_source=panel_source)
        new_report_event.genomicEntities = self.migrate_genomic_entities(genomic_entities=report_event.genomicEntities)
        new_report_event.variantClassification = self.migrate_variant_classification(classification=report_event.variantClassification)
        return self.validate_object(object_to_validate=new_report_event, object_type=self.new_model.ReportEvent)

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

    def migrate_variant_conseuqences(self, variant_consequences):
        return [self.migrate_variant_consequence(variant_consequence=variant_consequence) for variant_consequence in variant_consequences]

    def migrate_variant_consequence(self, variant_consequence):
        new_variant_consequence = self.convert_class(self.new_model.VariantConsequence, variant_consequence)
        return self.validate_object(object_to_validate=new_variant_consequence, object_type=self.new_model.VariantConsequence)

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

    def migrate_additional_analysis_panels(self, old_panels):
        return [self.migrate_additional_analysis_panel(old_panel=old_panel) for old_panel in old_panels]

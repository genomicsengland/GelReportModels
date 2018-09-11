import re
from protocols import reports_6_0_0
from protocols import reports_5_0_0
from protocols.migration.base_migration import MigrationError
from protocols.migration.base_migration import BaseMigrateReports500And600


class MigrateReports500To600(BaseMigrateReports500And600):

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
        new_instance.variants = self.convert_collection(
            list(zip(old_instance.variants, new_instance.variants)), self._migrate_variant, panel_source=panel_source)
        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretedGenome
        )

    def migrate_clinical_report_rd(self, old_instance):
        """
        :type old_instance: reports_5_0_0.ClinicalReportRD
        :rtype reports_6_0_0.ClinicalReport:
        """
        migrated_instance = self.convert_class(self.new_model.ClinicalReport, old_instance)
        if old_instance.variants is not None:
            migrated_instance.variants = self.convert_collection(
                list(zip(old_instance.variants, migrated_instance.variants)), self._migrate_variant)
        return self.validate_object(object_to_validate=migrated_instance, object_type=self.new_model.ClinicalReport)

    def migrate_rd_exit_questionnaire(self, old_instance, assembly):
        """
        :type old_instance: reports_5_0_0.RareDiseaseExitQuestionnaire
        :type assembly: reports_5_0_0.Assembly
        :rtype: reports_6_0_0.RareDiseaseExitQuestionnaire
        """
        if assembly is None:
            raise MigrationError("Parameter <assembly> is required to migrate exit questionnaire to version 6")
        migrated_instance = self.convert_class(self.new_model.RareDiseaseExitQuestionnaire, old_instance)
        migrated_instance.variantGroupLevelQuestions = self.convert_collection(
            old_instance.variantGroupLevelQuestions, self._migrate_variant_group_level_question, assembly=assembly)
        return self.validate_object(
            object_to_validate=migrated_instance, object_type=self.new_model.RareDiseaseExitQuestionnaire)

    def migrate_cancer_interpreted_genome(self, old_instance):
        """
        :type old_instance: reports_5_0_0.InterpretedGenomeRD
        :rtype: reports_6_0_0.InterpretedGenome
        """
        new_instance = self.convert_class(target_klass=self.new_model.InterpretedGenome, instance=old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        new_instance.variants = self.convert_collection(
            old_instance.variants, self.migrate_variant_cancer)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.InterpretedGenome)

    def migrate_cancer_clinical_report(self, old_instance):
        """
        :type old_instance: reports_5_0_0.ClinicalReportRD
        :rtype: reports_6_0_0.ClinicalReport
        """
        new_ccr = self.convert_class(target_klass=self.new_model.ClinicalReport, instance=old_instance)
        new_ccr.variants = self.convert_collection(
            old_instance.variants, self.migrate_variant_cancer)
        return self.validate_object(object_to_validate=new_ccr, object_type=self.new_model.ClinicalReport)

    def migrate_cancer_exit_questionnaire(self, old_instance, assembly):
        """
        :type old_instance: reports_5_0_0.CancerExitQuestionnaire
        :type assembly: reports_5_0_0.Assembly
        :rtype: reports_6_0_0.CancerExitQuestionnaire
        """
        if assembly is None:
            raise MigrationError(
                "Parameter <assembly> is required to migrate cancer exit questionnaire to version 6")

        new_c_eq = self.convert_class(target_klass=self.new_model.CancerExitQuestionnaire, instance=old_instance)
        new_c_eq.somaticVariantLevelQuestions = self.convert_collection(
            old_instance.somaticVariantLevelQuestions, self._migrate_somatic_variant_level_question, assembly=assembly)
        new_c_eq.germlineVariantLevelQuestions = self.convert_collection(
            old_instance.germlineVariantLevelQuestions, self._migrate_germline_variant_level_question, assembly=assembly)
        new_c_eq.otherActionableVariants = self.convert_collection(
            old_instance.otherActionableVariants, self._migrate_other_actionable_variant, assembly=assembly)
        return self.validate_object(object_to_validate=new_c_eq, object_type=self.new_model.CancerExitQuestionnaire)

    def _migrate_variant(self, variants, panel_source='panelapp'):
        old_instance = variants[0]
        new_instance = variants[1]
        new_instance.variantCalls = self.convert_collection(
            list(zip(old_instance.variantCalls, new_instance.variantCalls)), self._migrate_variant_call)
        consequence_types = []
        if old_instance.additionalTextualVariantAnnotations:
            consequence_types = old_instance.additionalTextualVariantAnnotations.get('ConsequenceType', "").split(",")
            consequence_types = [c for c in consequence_types if c]
        new_instance.reportEvents = self.convert_collection(
            list(zip(old_instance.reportEvents, new_instance.reportEvents)),
            self._migrate_report_event, panel_source=panel_source, consequence_types=consequence_types)
        new_instance.variantAttributes = self._migrate_variant_attributes(old_variant=old_instance)
        return new_instance

    def _migrate_variant_attributes(self, old_variant):
        # This logic is done here because alleleOrigins is part of the
        # v6 variantAttributes, which is non-nullable in v5 (or v6)
        # so the v5 variantAttributes could be null, but the alleleOrigins can not be,
        # so this is done to make sure we don't lose the alleleOrigins
        if old_variant.variantAttributes is not None:
            new_instance = self.convert_class(self.new_model.VariantAttributes, old_variant.variantAttributes)
            new_instance.fdp50 = self.convert_string_to_float(old_variant.variantAttributes.fdp50, fail=False)
        else:
            new_instance = self.new_model.VariantAttributes()

        new_instance.genomicChanges = old_variant.genomicChanges
        new_instance.cdnaChanges = old_variant.cdnaChanges
        new_instance.proteinChanges = old_variant.proteinChanges
        new_instance.additionalTextualVariantAnnotations = old_variant.additionalTextualVariantAnnotations
        new_instance.references = old_variant.references
        new_instance.additionalNumericVariantAnnotations = old_variant.additionalNumericVariantAnnotations
        new_instance.comments = old_variant.comments
        new_instance.alleleOrigins = old_variant.alleleOrigins
        new_instance.alleleFrequencies = self.convert_collection(
            old_variant.alleleFrequencies, self._migrate_allele_frequency)
        variant_identifiers = self.new_model.VariantIdentifiers(
            dbSnpId=old_variant.dbSnpId,
            cosmicIds=old_variant.cosmicIds,
            clinVarIds=old_variant.clinVarIds,
        )
        variant_identifiers = self.validate_object(object_to_validate=variant_identifiers, object_type=self.new_model.VariantIdentifiers)
        new_instance.variantIdentifiers = variant_identifiers
        return new_instance

    def _migrate_allele_frequency(self, old_frequency):
        new_frequency = self.convert_class(self.new_model.AlleleFrequency, old_frequency)
        return new_frequency

    def _migrate_variant_call(self, variant_calls):
        old_instance = variant_calls[0]
        new_instance = variant_calls[1]
        if old_instance.phaseSet:
            new_instance.phaseGenotype = self.new_model.PhaseGenotype()
            new_instance.phaseGenotype.phaseSet = old_instance.phaseSet
            # TODO: build this list or change the model or ...?
            new_instance.phaseGenotype.sortedAlleles = []
        new_instance.sampleVariantAlleleFrequency = old_instance.vaf
        return new_instance

    _tier1_consequence_types = [
        'transcript_ablation', 'splice_acceptor_variant', 'splice_donor_variant', 'stop_gained', 'frameshift_variant',
        'stop_lost', 'initiator_codon_variant']

    _tier2_consequence_types = [
        'transcript_amplification', 'inframe_insertion', 'inframe_deletion', 'missense_variant',
        'splice_region_variant', 'incomplete_terminal_codon_variant']

    _map_variant_consequences = {
        '3_prime_UTR_variant': 'SO:0001624',
        'splice_acceptor_variant': 'SO:0001574',
        'intergenic_variant': 'SO:0001628',
        'inframe_deletion': 'SO:0001822',
        'downstream_gene_variant': 'SO:0001632',
        'regulatory_region_amplification': 'SO:0001891',
        'initiator_codon_variant': 'SO:0001582',
        'TF_binding_site_variant': 'SO:0001782',
        '5_prime_UTR_variant': 'SO:0001623',
        'transcript_ablation': 'SO:0001893',
        'synonymous_variant': 'SO:0001819',
        'transcript_amplification': 'SO:0001889',
        'stop_retained_variant': 'SO:0001567',
        'protein_altering_variant': 'SO:0001818',
        'splice_donor_variant': 'SO:0001575',
        'inframe_insertion': 'SO:0001821',
        'stop_lost': 'SO:0001578',
        'feature_truncation': 'SO:0001906',
        'non_coding_transcript_variant': 'SO:0001619',
        'incomplete_terminal_codon_variant': 'SO:0001626',
        'inframe_variant': 'SO:0001650',
        'NMD_transcript_variant': 'SO:0001621',
        'non_coding_transcript_exon_variant': 'SO:0001792',
        'splice_region_variant': 'SO:0001630',
        'TFBS_ablation': 'SO:0001895',
        'stop_gained': 'SO:0001587',
        'coding_sequence_variant': 'SO:0001580',
        'upstream_gene_variant': 'SO:0001631',
        'regulatory_region_ablation': 'SO:0001894',
        'TFBS_amplification': 'SO:0001892',
        'start_lost': 'SO:0002012',
        'frameshift_variant': 'SO:0001589',
        'regulatory_region_variant': 'SO:0001566',
        'feature_elongation': 'SO:0001907',
        'missense_variant': 'SO:0001583',
        'mature_miRNA_variant': 'SO:0001620',
        'intron_variant': 'SO:0001627'
    }

    def _migrate_report_event(self, report_events, panel_source='panelapp', consequence_types=[]):
        old_instance = report_events[0]
        new_instance = report_events[1]
        new_instance.phenotypes = self._migrate_phenotypes(phenotypes=old_instance.phenotypes)
        new_instance.genePanel = self._migrate_gene_panel(
            (old_instance.genePanel, new_instance.genePanel), panel_source=panel_source)
        new_instance.genomicEntities = self.convert_collection(
            list(zip(old_instance.genomicEntities, new_instance.genomicEntities)), self._migrate_genomic_entity)
        new_instance.variantClassification = self._migrate_variant_classification(
            (old_instance.variantClassification, new_instance.variantClassification))
        if old_instance.eventJustification:
            new_instance.segregationPattern = self._migrate_segregation_pattern(
                event_justification=old_instance.eventJustification)
        if consequence_types is None:
            consequence_types = []
        tier = new_instance.tier
        is_tier1 = tier == self.new_model.Tier.TIER1
        is_tier2 = tier == self.new_model.Tier.TIER2
        is_tier3 = tier == self.new_model.Tier.TIER3
        new_instance.variantConsequences = list(map(
            lambda f: self.new_model.VariantConsequence(id=self._map_variant_consequences.get(f, ""), name=f), list(filter(
                lambda c: (is_tier1 and c in self._tier1_consequence_types) or \
                          (is_tier2 and c in self._tier2_consequence_types) or is_tier3, consequence_types))))
        return new_instance

    def _migrate_segregation_pattern(self, event_justification):
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

    def _migrate_gene_panel(self, gene_panels, panel_source='panelapp'):
        old_instance = gene_panels[0]
        new_instance = gene_panels[1]
        if old_instance is None:
            return None
        new_instance.source = panel_source
        return new_instance

    def _migrate_variant_classification(self, classifications):
        old_instance = classifications[0]
        new_instance = classifications[1]
        if old_instance is None:
            return None
        new_instance.clinicalSignificance = self._migrate_clinical_significance(
            old_significance=old_instance.clinicalSignificance)
        new_instance.drugResponseClassification = None
        return new_instance

    def _migrate_clinical_significance(self, old_significance):
        return self.clinical_signicance_map.get(old_significance)

    def _migrate_phenotypes(self, phenotypes):
        new_instance = self.new_model.Phenotypes(
            nonStandardPhenotype=phenotypes,
        )
        return new_instance

    def _migrate_genomic_entity(self, genomic_entities):
        old_instance = genomic_entities[0]
        new_instance = genomic_entities[1]
        if old_instance.otherIds is not None and isinstance(old_instance.otherIds, dict):
            new_instance.otherIds = self._migrate_other_ids(old_instance.otherIds)
        return new_instance

    def _migrate_other_ids(self, identifiers):
        if identifiers is None:
            return None
        new_identifiers = []
        for source, identifier in identifiers.items():
            new_identifiers.append(self.new_model.Identifier(
                source=source,
                identifier=identifier
            ))
        return new_identifiers

    def _migrate_variant_group_level_question(self, VGLQ, assembly):
        migrated_vglq = self.convert_class(target_klass=self.new_model.VariantGroupLevelQuestions, instance=VGLQ)
        migrated_vglq.variantLevelQuestions = self.convert_collection(
            VGLQ.variantLevelQuestions, self._migrate_variant_level_question, assembly=assembly)
        return migrated_vglq

    def _migrate_variant_level_question(self, vlq, assembly):
        migrated_vlq = self.convert_class(target_klass=self.new_model.VariantLevelQuestions, instance=vlq)
        migrated_vlq.variantCoordinates = self._migrate_variant_coordinates(
            variant_details=vlq.variantDetails, assembly=assembly
        )
        return migrated_vlq

    def _migrate_variant_coordinates(self, variant_details, assembly):
        details = self._extract_variant_details(variant_details=variant_details)
        variant_coordinates = self.new_model.VariantCoordinates(
            chromosome=details.get("chromosome"),
            position=details.get("position"),
            reference=details.get("reference"),
            alternate=details.get("alternate"),
            assembly=assembly,
        )
        return variant_coordinates

    @staticmethod
    def _extract_variant_details(variant_details):
        """
        The format of variant_details is "chr:pos:ref:alt"
        """
        details = list(map(lambda x: x.strip(), re.compile(":|>").split(variant_details)))
        if len(details) != 4:
            raise MigrationError("Variant details: {variant_details} should have fields chr, pos, ref and alt".format(
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

    def migrate_variant_cancer(self, variant):
        new_variant = self.convert_class(target_klass=self.new_model.SmallVariant, instance=variant)
        new_variant.variantCalls = self.convert_collection(
            list(zip(variant.variantCalls, new_variant.variantCalls)), self._migrate_variant_call)
        new_variant.reportEvents = self.convert_collection(
            list(zip(variant.reportEvents, new_variant.reportEvents)), self._migrate_report_event_cancer)
        new_variant.variantAttributes = self._migrate_variant_attributes(old_variant=variant)
        return self.validate_object(object_to_validate=new_variant, object_type=self.new_model.SmallVariant)

    def _migrate_report_event_cancer(self, report_events):
        old_instance = report_events[0]
        new_instance = report_events[1]
        new_instance.modeOfInheritance = self.new_model.ModeOfInheritance.na
        new_instance.phenotypes = self.new_model.Phenotypes()
        new_instance.genomicEntities = self.convert_collection(
            list(zip(old_instance.genomicEntities, new_instance.genomicEntities)), self._migrate_genomic_entity)
        new_instance.variantClassification = self._migrate_variant_classification(
            (old_instance.variantClassification, new_instance.variantClassification))
        # migrate tier to domain
        new_instance.tier = None
        if old_instance.tier:
            new_instance.domain = self.tier_domain_map[old_instance.tier]
        if old_instance.actions:
            new_instance.actions = self._migrate_actions(old_instance.actions)
        return new_instance

    def _migrate_actions(self, actions):

        def _extract_evidence_type(evidence_type):
            # conditions are extracted from the text between brackets in evidence type
            return list(map(lambda x: x.strip(), re.search(".*\((.*)\)", evidence_type).group(1).split(',')))

        new_actions = self.new_model.Actions()
        for action in actions:
            # map to either entity by the content of field evidence type
            if "Trial" in action.evidenceType:
                if action.url:  # NOTE: we need the url to extract the study identifier
                    trial = self.new_model.Trial()
                    trial.studyIdentifier = action.url.strip('/').split('/')[-1]
                    trial.studyUrl = action.url
                    trial.references = action.references
                    trial.variantActionable = action.variantActionable
                    trial.conditions = _extract_evidence_type(action.evidenceType)
                    if not new_actions.trials:
                        new_actions.trials = []
                    new_actions.trials.append(trial)
            elif "Prognostic" in action.evidenceType:
                prognosis = self.new_model.Prognosis()
                prognosis.referenceUrl = action.url or ""  # NOTE: it isn't frequent but there're some missing URLs
                prognosis.source = action.source
                prognosis.references = action.references
                prognosis.variantActionable = action.variantActionable
                prognosis.conditions = _extract_evidence_type(action.evidenceType)
                if not new_actions.prognosis:
                    new_actions.prognosis = []
                new_actions.prognosis.append(prognosis)
            elif "Therapeutic" in action.evidenceType:
                therapy = self.new_model.Therapy()
                therapy.referenceUrl = action.url or ""  # NOTE: it isn't frequent but there're some missing URLs
                therapy.source = action.source
                therapy.references = action.references
                therapy.variantActionable = action.variantActionable
                therapy.conditions = _extract_evidence_type(action.evidenceType)
                if not new_actions.therapies:
                    new_actions.therapies = []
                new_actions.therapies.append(therapy)
        return new_actions

    def _migrate_somatic_variant_level_question(self, question, assembly):
        new_instance = self.convert_class(target_klass=self.new_model.CancerSomaticVariantLevelQuestions, instance=question)
        new_instance.variantCoordinates = self._migrate_variant_coordinates(
            variant_details=question.variantDetails, assembly=assembly
        )
        return new_instance

    def _migrate_germline_variant_level_question(self, question, assembly):
        new_instance = self.convert_class(target_klass=self.new_model.CancerGermlineVariantLevelQuestions, instance=question)
        new_instance.variantCoordinates = self._migrate_variant_coordinates(
            variant_details=question.variantDetails, assembly=assembly
        )
        return new_instance

    def _migrate_other_actionable_variant(self, old_variant, assembly):
        new_instance = self.convert_class(target_klass=self.new_model.AdditionalVariantsQuestions, instance=old_variant)
        new_instance.variantCoordinates = self._migrate_variant_coordinates(
            variant_details=old_variant.variantDetails, assembly=assembly
        )
        return new_instance

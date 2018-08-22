import logging

from protocols import reports_4_0_0 as reports_4_0_0
from protocols import reports_5_0_0 as reports_5_0_0
from protocols.migration.base_migration import BaseMigration
from protocols.migration.base_migration import MigrationError
from protocols.migration.participants import MigrationParticipants110To100


class MigrateReports500To400(BaseMigration):

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
        feature_type = feature_type_map.get(entity.type)
        if feature_type is None:
            raise MigrationError(
                "{} can not be migrated to a feature type, but be one of: {}".format(
                    entity.type, feature_type_map.keys()
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
        genotype = genotype_map.get(variant_call.zygosity)
        if genotype is None:
            raise MigrationError("Can not migrate variant call to genotype when zygosity is: {}".format(
                variant_call.zygosity
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

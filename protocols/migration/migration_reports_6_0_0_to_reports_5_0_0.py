from protocols import reports_6_0_0
from protocols import reports_5_0_0
from protocols.migration.base_migration_reports_5_0_0_and_reports_6_0_0 import BaseMigrateReports500And600
from protocols.migration.base_migration import (
    BaseMigration,
    MigrationError,
)
from protocols.reports_6_0_0 import diseaseType, TissueSource


class MigrateReports600To500(BaseMigrateReports500And600):

    old_model = reports_6_0_0
    new_model = reports_5_0_0

    def migrate_interpretation_request_rd(self, old_instance):
        """
        Migrates a reports_6_0_0.InterpretationRequestRD into a reports_5_0_0.InterpretationRequestRD
        :type old_instance: reports_6_0_0.InterpretationRequestRD
        :rtype: reports_5_0_0.InterpretationRequestRD
        """
        new_instance = self.convert_class(self.new_model.InterpretationRequestRD, old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD
        )

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
        new_instance.variants = self.migrate_variants_cancer(variants=old_instance.variants)

        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.CancerInterpretedGenome)

    def migrate_variants_cancer(self, variants):
        if variants:
            return [self.migrate_variant_cancer(old_variant) for old_variant in variants]

    def migrate_variant_cancer(self, old_variant):
        new_variant = self.convert_class(self.new_model.ReportedVariantCancer, old_variant)
        attributes = old_variant.variantAttributes.toJsonDict()
        new_variant.updateWithJsonDict(attributes)
        new_variant.variantAttributes.fdp50 = str(old_variant.variantAttributes.fdp50)

        identifiers = old_variant.variantAttributes.variantIdentifiers.toJsonDict()
        new_variant.updateWithJsonDict(identifiers)

        new_variant.variantCalls = [self.migrate_variant_call_cancer(call) for call in old_variant.variantCalls]
        new_variant.reportEvents = [self.migrate_report_event_cancer(reportEvent) for reportEvent in old_variant.reportEvents]

        return new_variant

    def migrate_variant_call_cancer(self, old_variant_call):
        new_variant_call = self.convert_class(self.new_model.VariantCall, old_variant_call)
        if old_variant_call.phaseGenotype:
            new_variant_call.phaseSet = old_variant_call.phaseGenotype.phaseSet
        new_variant_call.vaf = old_variant_call.sampleVariantAlleleFrequency
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
        return self.validate_object(object_to_validate=new_variant_classification, object_type=self.new_model.VariantClassification)

    def migrate_clinical_significance(self, old_significance):
        return self.clinical_signicance_reverse_map.get(old_significance)

    def migrate_genomic_entity(self, genomic_entity):
        new_genomic_entity = self.convert_class(self.new_model.GenomicEntity, genomic_entity)
        if genomic_entity.otherIds is not None:
            new_genomic_entity.otherIds = \
                {identifier.source: identifier.identifier for identifier in genomic_entity.otherIds}
        return self.validate_object(object_to_validate=new_genomic_entity, object_type=self.new_model.GenomicEntity)

    def migrate_actions(self, actions):
        if not actions:
            return []
        evidences = [("Trial", actions.trials), ("Prognostic", actions.prognosis), ("Therapeutic", actions.therapies)]
        present_evidences = [(typ, evidence) for typ, evidence in evidences if evidence]
        return [self._make_action_from(e, typ) for typ, evidence in present_evidences for e in evidence]

    def _make_action_from(self, evidence, evidenceType):
        action = self.new_model.Action()
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

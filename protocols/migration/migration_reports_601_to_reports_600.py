from protocols import reports_6_0_0, reports_6_0_1
from protocols.migration import BaseMigration


class MigrateReports601To600(BaseMigration):

    old_model = reports_6_0_1
    new_model = reports_6_0_0

    def migrate_interpretation_request_rd(self, old_instance):
        """
        Migrates a reports_6_0_1.InterpretationRequestRD into a reports_6_0_0.InterpretationRequestRD
        :type old_instance: reports_6_0_0.InterpretationRequestRD
        :rtype: reports_6_0_0.InterpretationRequestRD
        """
        new_instance = self.convert_class(target_klass=self.new_model.InterpretationRequestRD, instance=old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        new_flags = []
        if new_instance.interpretationFlags:
            for flag in new_instance.interpretationFlags:
                if getattr(reports_6_0_0.InterpretationFlags, flag.interpretationFlag, False):
                    new_flags.append(flag)
                else:
                    new_flags.append(reports_6_0_0.InterpretationFlag(
                        interpretationFlag=reports_6_0_0.InterpretationFlags.other,
                        additionalDescription=flag.interpretationFlag
                    ))
            new_instance.interpretationFlags = new_flags
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD)

    def migrate_exit_questionnaire_rd(self, old_instance):
        """
        Migrates a reports_6_0_1.RareDiseaseExitQuestionnaire to a reports_6_0_0.RareDiseaseExitQuestionnaire
        :type old_instance: reports_6_0_1.RareDiseaseExitQuestionnaire
        :rtype: reports_6_0_0.RareDiseaseExitQuestionnaire
        """
        new_instance = self.convert_class(
            target_klass=self.new_model.RareDiseaseExitQuestionnaire, instance=old_instance)
        if new_instance.variantGroupLevelQuestions is None:
            new_instance.variantGroupLevelQuestions = []
        for variant_gl in new_instance.variantGroupLevelQuestions:
            for variant in variant_gl.variantLevelQuestions:
                if variant.acmgClassification == 'na':
                    variant.acmgClassification = 'not_assessed'
        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.RareDiseaseExitQuestionnaire)

    def migrate_exit_questionnaire_cancer(self, old_instance):
        """
        Migrates a reports_6_0_1.CancerExitQuestionnaire to a reports_6_0_0.CancerExitQuestionnaire
        :type old_instance: reports_6_0_1.CancerExitQuestionnaire
        :rtype: reports_6_0_0.CancerExitQuestionnaire
        """
        new_instance = self.convert_class(
            target_klass=self.new_model.CancerExitQuestionnaire, instance=old_instance)
        if new_instance.caseLevelQuestions.reviewedInMdtWga == 'somatic_if_relevant':
            new_instance.caseLevelQuestions.reviewedInMdtWga = 'domain_1'

        if new_instance.caseLevelQuestions.actionableVariants == 'na':
            new_instance.caseLevelQuestions.actionableVariants = 'no'

        list_of_actionable_variants = []
        for actionable_variant in new_instance.otherActionableVariants:
            if actionable_variant.variantCoordinates is not None:
                list_of_actionable_variants.append(actionable_variant)

        new_instance.otherActionableVariants = list_of_actionable_variants
        return self.validate_object(
            object_to_validate=new_instance, object_type=self.new_model.CancerExitQuestionnaire)

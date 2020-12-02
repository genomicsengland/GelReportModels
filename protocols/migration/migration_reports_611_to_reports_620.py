from protocols import reports_6_1_1, reports_6_2_0
from protocols.reports_6_2_0 import UserComment
from protocols.migration import BaseMigration


class MigrateReports611To620(BaseMigration):

    old_model = reports_6_1_1
    new_model = reports_6_2_0

    def migrate_variant_interpretation_log(self, old_instance):
        """
        Migrates a reports_6_1_1.VariantInterpretationLog into a reports_6_2_0.VariantInterpretationLog
        :type old_instance: reports_6_1_1.VariantInterpretationLog
        :rtype: reports_6_2_0.VariantInterpretationLog
        """
        new_instance = self.convert_class(target_klass=self.new_model.VariantInterpretationLog, instance=old_instance)
        if new_instance.variantClassification.acmgVariantClassification:
            for acmg_evidence in new_instance.variantClassification.acmgVariantClassification.acmgEvidences:
                if acmg_evidence.type == "bening":
                    acmg_evidence.type = "benign"
                # activation strength is now a required field. Previously it was optional, only to be used if different from weight
                # If activationStrength not populated, set it to the same as weight
                if not acmg_evidence.activationStrength:
                    acmg_evidence.activationStrength = acmg_evidence.weight
        if old_instance.comments:
            new_instance.comments = [UserComment(comment=comment) for comment in old_instance.comments]
        new_instance.groupId = old_instance.familyId
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.VariantInterpretationLog)

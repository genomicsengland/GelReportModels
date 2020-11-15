from protocols import reports_6_1_1, reports_6_2_0
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
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.VariantInterpretationLog)

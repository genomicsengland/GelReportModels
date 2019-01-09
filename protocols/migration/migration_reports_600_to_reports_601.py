from protocols import reports_6_0_0, reports_6_0_1
from protocols.migration import BaseMigration


class MigrateReports600To601(BaseMigration):

    old_model = reports_6_0_0
    new_model = reports_6_0_1

    def migrate_interpretation_request_rd(self, old_instance):
        """
        Migrates a reports_6_0_0.InterpretationRequestRD into a reports_6_0_1.InterpretationRequestRD
        :type old_instance: reports_6_0_0.InterpretationRequestRD
        :rtype: reports_6_0_1.InterpretationRequestRD
        """
        new_instance = self.convert_class(target_klass=self.new_model.InterpretationRequestRD, instance=old_instance)
        new_instance.versionControl = self.new_model.ReportVersionControl()
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.InterpretationRequestRD)


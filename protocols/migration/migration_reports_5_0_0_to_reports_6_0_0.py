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

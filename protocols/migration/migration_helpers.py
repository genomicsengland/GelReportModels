import logging

from protocols.migration.base_migration import MigrationError

from protocols.reports_2_1_0 import ClinicalReportRD as ClinicalReportRD_2_1_0
from protocols.reports_2_1_0 import InterpretedGenomeRD as InterpretedGenomeRD_2_1_0
from protocols.reports_2_1_0 import InterpretationRequestRD as InterpretationRequestRD_2_1_0

from protocols.reports_3_0_0 import ClinicalReportRD as ClinicalReportRD_3_0_0
from protocols.reports_3_0_0 import InterpretedGenomeRD as InterpretedGenomeRD_3_0_0
from protocols.reports_3_0_0 import InterpretationRequestRD as InterpretationRequestRD_3_0_0
from protocols.reports_3_0_0 import CancerInterpretationRequest as CancerInterpretationRequest_3_0_0
from protocols.reports_3_0_0 import RareDiseaseExitQuestionnaire as RareDiseaseExitQuestionnaire_3_0_0

from protocols.reports_4_0_0 import ClinicalReportCancer as ClinicalReportCancer_4_0_0
from protocols.reports_4_0_0 import ClinicalReportRD as ClinicalReportRD_4_0_0
from protocols.reports_4_0_0 import InterpretationRequestRD as InterpretationRequestRD_4_0_0
from protocols.reports_4_0_0 import InterpretedGenomeRD as InterpretedGenomeRD_4_0_0
from protocols.reports_4_0_0 import CancerInterpretedGenome as CancerInterpretedGenome_4_0_0
from protocols.reports_4_0_0 import CancerInterpretationRequest as CancerInterpretationRequest_4_0_0

from protocols.reports_5_0_0 import ClinicalReportRD as ClinicalReportRD_5_0_0
from protocols.reports_5_0_0 import InterpretedGenomeRD as InterpretedGenomeRD_5_0_0
from protocols.reports_5_0_0 import ClinicalReportCancer as ClinicalReportCancer_5_0_0
from protocols.reports_5_0_0 import CancerExitQuestionnaire as CancerExitQuestionnaire_5_0_0
from protocols.reports_5_0_0 import InterpretationRequestRD as InterpretationRequestRD_5_0_0
from protocols.reports_5_0_0 import CancerInterpretedGenome as CancerInterpretedGenome_5_0_0
from protocols.reports_5_0_0 import CancerInterpretationRequest as CancerInterpretationRequest_5_0_0
from protocols.reports_5_0_0 import RareDiseaseExitQuestionnaire as RareDiseaseExitQuestionnaire_5_0_0

from protocols.reports_6_0_0 import ClinicalReport as ClinicalReport_6_0_0
from protocols.reports_6_0_0 import InterpretedGenome as InterpretedGenome_6_0_0
from protocols.reports_6_0_0 import CancerExitQuestionnaire as CancerExitQuestionnaire_6_0_0
from protocols.reports_6_0_0 import InterpretationRequestRD as InterpretationRequestRD_6_0_0
from protocols.reports_6_0_0 import CancerInterpretationRequest as CancerInterpretationRequest_6_0_0
from protocols.reports_6_0_0 import RareDiseaseExitQuestionnaire as RareDiseaseExitQuestionnaire_6_0_0

from protocols.participant_1_1_0 import Pedigree as Pedigree_1_1_0
from protocols.participant_1_0_3 import Pedigree as Pedigree_1_0_3
from protocols.participant_1_0_0 import Pedigree as Pedigree_1_0_0
from protocols.reports_3_0_0 import Pedigree as Pedigree_reports_3_0_0

from protocols.participant_1_1_0 import CancerParticipant as CancerParticipant_1_1_0
from protocols.participant_1_0_3 import CancerParticipant as CancerParticipant_1_0_3
from protocols.participant_1_0_0 import CancerParticipant as CancerParticipant_1_0_0

from protocols.migration.model_validator import PayloadValidation
from protocols.migration.migration import Migration2_1To3
from protocols.migration.migration_reports_3_0_0_to_reports_4_0_0 import MigrateReports3To4
from protocols.migration.migration_reports_4_0_0_to_reports_5_0_0 import MigrateReports400To500
from protocols.migration.migration_reports_5_0_0_to_reports_6_0_0 import MigrateReports500To600
from protocols.migration.migration_reports_4_0_0_to_reports_3_0_0 import MigrateReports400To300
from protocols.migration import MigrateReports500To400
from protocols.migration.participants import (
    MigrationReportsToParticipants1,
    MigrationParticipants100To103,
    MigrationParticipants103To110,
)
from protocols.reports_5_0_0 import Assembly


class MigrationHelpers(object):

    @staticmethod
    def migrate_interpretation_request_rd_to_latest(json_dict, assembly=None):
        """
        :type json_dict: dict
        :type assembly: Assembly
        :rtype: InterpretationRequestRD_5_0_0
        """
        types = [
            InterpretationRequestRD_6_0_0,
            InterpretationRequestRD_5_0_0,
            InterpretationRequestRD_4_0_0,
            InterpretationRequestRD_3_0_0,
            InterpretationRequestRD_2_1_0
        ]

        migrations = [
            MigrationHelpers.set_version_to_6_0_0,  # needed because 5 is valid as 6
            MigrateReports500To600().migrate_interpretation_request_rd,
            lambda x: MigrateReports400To500().migrate_interpretation_request_rd(old_instance=x, assembly=assembly),
            MigrateReports3To4().migrate_interpretation_request_rd,
            Migration2_1To3().migrate_interpretation_request
        ]

        return MigrationHelpers.migrate(json_dict, types, migrations)

    @staticmethod
    def migrate_interpretation_request_rd_to_interpreted_genome_latest(json_dict, assembly):
        """
        :type json_dict: dict
        :type assembly: Assembly
        :rtype: InterpretedGenomeRD_5_0_0
        """
        types = [
            InterpretationRequestRD_6_0_0,
            InterpretationRequestRD_5_0_0,
            InterpretationRequestRD_4_0_0,
            InterpretationRequestRD_3_0_0,
            InterpretationRequestRD_2_1_0
        ]

        migrations = [
            lambda x: x,
            MigrateReports500To600().migrate_interpreted_genome_rd,
            lambda x: MigrateReports400To500().migrate_interpretation_request_rd_to_interpreted_genome_rd(
                old_instance=x, assembly=assembly, interpretation_service="tiering",
                reference_database_versions={}, software_versions={}
            ),
            MigrateReports3To4().migrate_interpretation_request_rd,
            Migration2_1To3().migrate_interpretation_request
        ]

        return MigrationHelpers.migrate(json_dict, types, migrations)

    @staticmethod
    def migrate_interpreted_genome_rd_to_latest(
            json_dict, assembly=None, interpretation_request_version=None, panel_source='panelapp'):
        """
        :type json_dict: dict
        :type assembly: Assembly
        :type interpretation_request_version: int
        :type panel_source: str
        :rtype: InterpretedGenomeRD_5_0_0
        """
        types = [
            InterpretedGenome_6_0_0,
            InterpretedGenomeRD_5_0_0,
            InterpretedGenomeRD_4_0_0,
            InterpretedGenomeRD_3_0_0,
            InterpretedGenomeRD_2_1_0
        ]

        migrations = [
            lambda x: x,
            lambda x: MigrateReports500To600().migrate_interpreted_genome_rd(x, panel_source=panel_source),
            lambda x: MigrateReports400To500().migrate_interpreted_genome_rd(
                x, assembly=assembly, interpretation_request_version=interpretation_request_version),
            MigrateReports3To4().migrate_interpreted_genome_rd,
            Migration2_1To3().migrate_interpreted_genome
        ]

        return MigrationHelpers.migrate(json_dict, types, migrations)

    @staticmethod
    def migrate_clinical_report_rd_to_latest(json_dict, assembly=None):
        """
        :type json_dict: dict
        :type assembly: Assembly
        :rtype: ClinicalReportRD_5_0_0
        """
        types = [
            ClinicalReport_6_0_0,
            ClinicalReportRD_5_0_0,
            ClinicalReportRD_4_0_0,
            ClinicalReportRD_3_0_0,
            ClinicalReportRD_2_1_0
        ]

        migrations = [
            lambda x: x,
            MigrateReports500To600().migrate_clinical_report_rd,
            lambda x: MigrateReports400To500().migrate_clinical_report_rd(old_instance=x, assembly=assembly),
            MigrateReports3To4().migrate_clinical_report_rd,
            Migration2_1To3().migrate_clinical_report
        ]

        return MigrationHelpers.migrate(json_dict, types, migrations)

    @staticmethod
    def migrate_exit_questionnaire_rd_to_latest(json_dict, assembly):
        """
        There are no changes in exit questionnaires between versions 4 and 5
        :type json_dict: dict
        :type assembly: str
        :rtype: RareDiseaseExitQuestionnaire_5_0_0
        """
        types = [
            RareDiseaseExitQuestionnaire_6_0_0,
            RareDiseaseExitQuestionnaire_5_0_0,
            RareDiseaseExitQuestionnaire_3_0_0
        ]

        migrations = [
            lambda x: x,
            lambda x: MigrateReports500To600().migrate_rd_exit_questionnaire(old_instance=x, assembly=assembly),
            MigrateReports3To4().migrate_rd_exit_questionnaire
        ]

        return MigrationHelpers.migrate(json_dict, types, migrations)

    @staticmethod
    def migrate_cancer_exit_questionnaire_to_latest(json_dict, assembly):
        """
        No data exists for Cancer Exit Questionnaires in v4.2.0 of the models
        :type json_dict: dict
        :type assembly: str
        :rtype: CancerExitQuestionnaire_6_0_0
        """
        types = [
            CancerExitQuestionnaire_6_0_0,
            CancerExitQuestionnaire_5_0_0
        ]

        migrations = [
            lambda x: x,
            lambda x: MigrateReports500To600().migrate_cancer_exit_questionnaire(old_instance=x, assembly=assembly)
        ]

        return MigrationHelpers.migrate(json_dict, types, migrations)

    @staticmethod
    def migrate_pedigree_to_latest(json_dict):
        """
        :type json_dict: dict
        :rtype: Pedigree_1_1_0
        """
        types = [
            Pedigree_1_1_0,
            Pedigree_1_0_3,
            Pedigree_1_0_0,
            Pedigree_reports_3_0_0
        ]

        migrations = [
            lambda x: x,
            MigrationParticipants103To110().migrate_pedigree,
            MigrationParticipants100To103().migrate_pedigree,
            MigrationReportsToParticipants1().migrate_pedigree
        ]

        return MigrationHelpers.migrate(json_dict, types, migrations)

    @staticmethod
    def migrate_interpretation_request_cancer_to_latest(json_dict, assembly):
        """
        :type json_dict: dict
        :type assembly: Assembly
        :rtype: CancerInterpretationRequest_5_0_0
        """
        types = [
            CancerInterpretationRequest_6_0_0,
            CancerInterpretationRequest_5_0_0,
            CancerInterpretationRequest_4_0_0,
            CancerInterpretationRequest_3_0_0
        ]

        migrations = [
            MigrationHelpers.set_version_to_6_0_0,
            MigrateReports500To600().migrate_interpretation_request_cancer,
            lambda x: MigrateReports400To500().migrate_cancer_interpretation_request(old_instance=x, assembly=assembly),
            MigrateReports3To4().migrate_cancer_interpretation_request
        ]

        return MigrationHelpers.migrate(json_dict, types, migrations)

    @staticmethod
    def migrate_interpretation_request_cancer_to_interpreted_genome_latest(
            json_dict, assembly, interpretation_service, reference_database_versions, software_versions,
            report_url, comments):
        """
        :type json_dict: dict
        :type assembly: Assembly
        :type interpretation_service: str
        :type reference_database_versions: dict
        :type software_versions: dict
        :type report_url: str
        :type comments: list
        :rtype: CancerInterpretationRequest_5_0_0
        """
        if PayloadValidation(klass=CancerInterpretationRequest_5_0_0, payload=json_dict).is_valid or \
           PayloadValidation(klass=CancerInterpretationRequest_6_0_0, payload=json_dict).is_valid:
            raise MigrationError(
                "Cannot transform a cancer interpretation request in version 5.0.0 or 6.0.0 into an interpreted genome")

        types = [
            CancerInterpretationRequest_5_0_0,
            CancerInterpretationRequest_4_0_0,
            CancerInterpretationRequest_3_0_0
        ]

        migrations = [
            lambda x: x,
            lambda x: MigrateReports400To500().migrate_cancer_interpretation_request_to_cancer_interpreted_genome(
                old_instance=x, assembly=assembly, interpretation_service=interpretation_service,
                reference_database_versions=reference_database_versions, software_versions=software_versions,
                report_url=report_url, comments=comments),
            MigrateReports3To4().migrate_cancer_interpretation_request
        ]

        return MigrationHelpers.migrate(json_dict, types, migrations)

    @staticmethod
    def migrate_interpreted_genome_cancer_to_latest(json_dict, assembly=None, participant_id=None,
                                                    sample_id=None, interpretation_request_version=None,
                                                    interpretation_service=None):
        """
        Migration from reports 3.0.0 is not supported as we have no data in that version
        :type json_dict: dict
        :type assembly: Assembly
        :type participant_id: str
        :type sample_id: str
        :type interpretation_request_version: int
        :type interpretation_service: str
        :rtype: CancerInterpretedGenome_6_0_0
        """
        types = [
            InterpretedGenome_6_0_0,
            CancerInterpretedGenome_5_0_0,
            CancerInterpretedGenome_4_0_0
        ]

        migrations = [
            lambda x: x,
            MigrateReports500To600().migrate_cancer_interpreted_genome,
            lambda x: MigrateReports400To500().migrate_cancer_interpreted_genome(
                old_instance=x, assembly=assembly, participant_id=participant_id, sample_id=sample_id,
                interpretation_request_version=interpretation_request_version,
                interpretation_service=interpretation_service
            )
        ]

        return MigrationHelpers.migrate(json_dict, types, migrations)

    @staticmethod
    def migrate_clinical_report_cancer_to_latest(json_dict, sample_id=None, assembly=None, participant_id=None):
        """
        Migration from reports 3.0.0 is not supported as we have no data in that version
        :type json_dict: dict
        :type sample_id: str
        :type assembly: Assembly
        :type participant_id: str
        :rtype: ClinicalReport_6_0_0
        """
        types = [
            ClinicalReport_6_0_0,
            ClinicalReportCancer_5_0_0,
            ClinicalReportCancer_4_0_0
        ]

        migrations = [
            lambda x: x,
            MigrateReports500To600().migrate_cancer_clinical_report,
            lambda x: MigrateReports400To500().migrate_cancer_clinical_report(
                old_instance=x, assembly=assembly, participant_id=participant_id, sample_id=sample_id
            )
        ]

        return MigrationHelpers.migrate(json_dict, types, migrations)

    @staticmethod
    def migrate_cancer_participant_to_latest(json_dict):
        """
        :type json_dict: dict
        :rtype: CancerParticipant_1_1_0
        """
        types = [
            CancerParticipant_1_1_0,
            CancerParticipant_1_0_3,
            CancerParticipant_1_0_0
        ]

        migrations = [
            lambda x: x,
            MigrationParticipants103To110().migrate_cancer_participant,
            MigrationParticipants100To103().migrate_cancer_participant
        ]

        return MigrationHelpers.migrate(json_dict, types, migrations)

    @staticmethod
    def reverse_migrate_RD_clinical_report_to_v3(json_dict):
        """
        Whether html or json, the clinical report data needs to be migrated from v5 to v3 for RD
        :param json_dict: ClinicalReport RD v(5,4,3) json
        :return: ClinicalReport model object with cr.clinical_report_data migrated from v(5,4,3) to v3
        """
        types = [
            ClinicalReportRD_3_0_0,
            ClinicalReportRD_4_0_0,
            ClinicalReportRD_5_0_0
        ]

        migrations = [
            lambda x: x,
            MigrateReports400To300().migrate_clinical_report_rd,
            MigrateReports500To400().migrate_clinical_report_rd
        ]

        return MigrationHelpers.migrate(json_dict, types, migrations)

    @staticmethod
    def migrate(json_dict, types, migrations):
        for i, typ in enumerate(types):
            if PayloadValidation(klass=typ, payload=json_dict).is_valid:
                migrated = typ.fromJsonDict(json_dict)
                migrations_to_apply = migrations[0:i+1]
                for migration in reversed(migrations_to_apply):
                    migrated = migration(migrated)
                return migrated

        raise MigrationError("json_dict data is not one of: {}".format(types))

    @staticmethod
    def set_version_to_6_0_0(version_controlled):
        version_controlled.versionControl.gitVersionControl = "6.0.0"
        return version_controlled

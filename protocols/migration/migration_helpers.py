import logging

from protocols.migration.base_migration import MigrationError

from protocols.reports_2_1_0 import ClinicalReportRD as ClinicalReportRD_2_1_0
from protocols.reports_2_1_0 import InterpretedGenomeRD as InterpretedGenomeRD_2_1_0
from protocols.reports_2_1_0 import ClinicalReportCancer as ClinicalReportCancer_2_1_0
from protocols.reports_2_1_0 import InterpretationRequestRD as InterpretationRequestRD_2_1_0


from protocols.reports_3_0_0 import ClinicalReportRD as ClinicalReportRD_3_0_0
from protocols.reports_3_0_0 import InterpretedGenomeRD as InterpretedGenomeRD_3_0_0
from protocols.reports_3_0_0 import ClinicalReportCancer as ClinicalReportCancer_3_0_0
from protocols.reports_3_0_0 import InterpretationRequestRD as InterpretationRequestRD_3_0_0
from protocols.reports_3_0_0 import CancerInterpretationRequest as CancerInterpretationRequest_3_0_0
from protocols.reports_3_0_0 import RareDiseaseExitQuestionnaire as RareDiseaseExitQuestionnaire_3_0_0

from protocols.reports_4_0_0 import ClinicalReportCancer as ClinicalReportCancer_4_0_0
from protocols.reports_4_0_0 import ClinicalReportRD as ClinicalReportRD_4_0_0
from protocols.reports_4_0_0 import InterpretationRequestRD as InterpretationRequestRD_4_0_0
from protocols.reports_4_0_0 import InterpretedGenomeRD as InterpretedGenomeRD_4_0_0
from protocols.reports_4_0_0 import CancerInterpretedGenome as CancerInterpretedGenome_4_0_0
from protocols.reports_4_0_0 import CancerInterpretationRequest as CancerInterpretationRequest_4_0_0
from protocols.reports_4_0_0 import RareDiseaseExitQuestionnaire as RareDiseaseExitQuestionnaire_4_0_0

from protocols.reports_5_0_0 import Assembly as Assembly_5_0_0
from protocols.reports_5_0_0 import ClinicalReportRD as ClinicalReportRD_5_0_0
from protocols.reports_5_0_0 import InterpretedGenomeRD as InterpretedGenomeRD_5_0_0
from protocols.reports_5_0_0 import ClinicalReportCancer as ClinicalReportCancer_5_0_0
from protocols.reports_5_0_0 import InterpretationRequestRD as InterpretationRequestRD_5_0_0
from protocols.reports_5_0_0 import CancerInterpretedGenome as CancerInterpretedGenome_5_0_0
from protocols.reports_5_0_0 import CancerInterpretationRequest as CancerInterpretationRequest_5_0_0
from protocols.reports_5_0_0 import RareDiseaseExitQuestionnaire as RareDiseaseExitQuestionnaire_5_0_0
from protocols.reports_5_0_0 import CancerExitQuestionnaire as CancerExitQuestionnaire_5_0_0

from protocols.participant_1_1_0 import Pedigree as Pedigree_1_1_0
from protocols.participant_1_0_3 import Pedigree as Pedigree_1_0_3
from protocols.participant_1_0_0 import Pedigree as Pedigree_1_0_0
from protocols.reports_3_0_0 import Pedigree as Pedigree_reports_3_0_0

from protocols.participant_1_1_0 import CancerParticipant as CancerParticipant_1_1_0
from protocols.participant_1_0_3 import CancerParticipant as CancerParticipant_1_0_3
from protocols.participant_1_0_0 import CancerParticipant as CancerParticipant_1_0_0
from protocols.reports_3_0_0 import CancerParticipant as CancerParticipant_reports_3_0_0

from protocols.migration.model_validator import PayloadValidation
from protocols.migration.migration import Migration2_1To3
from protocols.migration.migration_reports_3_0_0_to_reports_4_0_0 import MigrateReports3To4
from protocols.migration.migration_reports_4_0_0_to_reports_5_0_0 import MigrateReports400To500
from protocols.migration.participants import \
    MigrationReportsToParticipants1, MigrationParticipants100To103, MigrationParticipants103To110

from protocols.reports_5_0_0 import Assembly


class MigrationHelpers(object):

    @staticmethod
    def migrate_interpretation_request_rd_to_latest(json_dict, assembly):
        """
        :type json_dict: dict
        :type assembly: Assembly
        :rtype: InterpretationRequestRD_5_0_0
        """
        ir_v500 = None

        if PayloadValidation(klass=InterpretationRequestRD_5_0_0, payload=json_dict).is_valid:
            ir_v500 = InterpretedGenomeRD_5_0_0.fromJsonDict(jsonDict=json_dict)
            logging.info("Case in models reports 5.0.0")

        elif PayloadValidation(klass=InterpretationRequestRD_4_0_0, payload=json_dict).is_valid:
            ir_v400 = InterpretationRequestRD_4_0_0.fromJsonDict(jsonDict=json_dict)
            ir_v500 = MigrateReports400To500().migrate_interpretation_request_rd(
                old_instance=ir_v400, assembly=assembly)
            logging.info("Case in models reports 4.0.0")

        elif PayloadValidation(klass=InterpretationRequestRD_3_0_0, payload=json_dict).is_valid:
            ir_v3 = InterpretationRequestRD_3_0_0.fromJsonDict(jsonDict=json_dict)
            ir_v400 = MigrateReports3To4().migrate_interpretation_request_rd(old_instance=ir_v3)
            ir_v500 = MigrateReports400To500().migrate_interpretation_request_rd(
                old_instance=ir_v400, assembly=assembly)
            logging.info("Case in models reports 3.0.0")

        elif PayloadValidation(klass=InterpretationRequestRD_2_1_0, payload=json_dict).is_valid:
            ir_v2 = InterpretationRequestRD_2_1_0.fromJsonDict(jsonDict=json_dict)
            ir_v3 = Migration2_1To3().migrate_interpretation_request(interpretation_request=ir_v2)
            ir_v400 = MigrateReports3To4().migrate_interpretation_request_rd(old_instance=ir_v3)
            ir_v500 = MigrateReports400To500().migrate_interpretation_request_rd(
                old_instance=ir_v400, assembly=assembly)
            logging.info("Case in models reports 2.1.0")

        if ir_v500 is not None:
            return ir_v500

        raise MigrationError("Interpretation Request RD is not in versions: [2.1.0, 3.0.0, 4.0.0, 5.0.0]")

    @staticmethod
    def migrate_interpretation_request_rd_to_interpreted_genome_latest(json_dict, assembly):
        """
        :type json_dict: dict
        :type assembly: Assembly
        :rtype: InterpretedGenomeRD_5_0_0
        """
        ir_v500 = None

        if PayloadValidation(klass=InterpretedGenomeRD_5_0_0, payload=json_dict).is_valid:
            ir_v500 = InterpretedGenomeRD_5_0_0.fromJsonDict(jsonDict=json_dict)
            logging.info("Case in models reports 5.0.0")

        elif PayloadValidation(klass=InterpretationRequestRD_4_0_0, payload=json_dict).is_valid:
            ir_v400 = InterpretationRequestRD_4_0_0.fromJsonDict(jsonDict=json_dict)
            ir_v500 = MigrateReports400To500().migrate_interpretation_request_rd_to_interpreted_genome_rd(
                old_instance=ir_v400, assembly=assembly, interpretation_service="tiering",
                reference_database_versions={}, software_versions={}
            )
            logging.info("Case in models reports 4.0.0")

        elif PayloadValidation(klass=InterpretationRequestRD_3_0_0, payload=json_dict).is_valid:
            ir_v3 = InterpretationRequestRD_3_0_0.fromJsonDict(jsonDict=json_dict)
            ir_v400 = MigrateReports3To4().migrate_interpretation_request_rd(old_instance=ir_v3)
            ir_v500 = MigrateReports400To500().migrate_interpretation_request_rd_to_interpreted_genome_rd(
                old_instance=ir_v400, assembly=assembly, interpretation_service="tiering",
                reference_database_versions={}, software_versions={}
            )
            logging.info("Case in models reports 3.0.0")

        elif PayloadValidation(klass=InterpretationRequestRD_2_1_0, payload=json_dict).is_valid:
            ir_v2 = InterpretationRequestRD_2_1_0.fromJsonDict(jsonDict=json_dict)
            ir_v3 = Migration2_1To3().migrate_interpretation_request(interpretation_request=ir_v2)
            ir_v400 = MigrateReports3To4().migrate_interpretation_request_rd(old_instance=ir_v3)
            ir_v500 = MigrateReports400To500().migrate_interpretation_request_rd_to_interpreted_genome_rd(
                old_instance=ir_v400, assembly=assembly, interpretation_service="tiering",
                reference_database_versions={}, software_versions={}
            )
            logging.info("Case in models reports 2.1.0")

        if ir_v500 is not None:
            return ir_v500

        raise MigrationError("Interpretation Request RD is not in versions: [2.1.0, 3.0.0, 4.0.0, 5.0.0]")

    @staticmethod
    def migrate_interpreted_genome_rd_to_latest(json_dict, assembly, interpretation_request_version):
        """
        :type json_dict: dict
        :type assembly: Assembly
        :type interpretation_request_version: int
        :rtype: InterpretedGenomeRD_5_0_0
        """
        ig_v500 = None

        if PayloadValidation(klass=InterpretedGenomeRD_5_0_0, payload=json_dict).is_valid:
            ig_v500 = InterpretedGenomeRD_5_0_0.fromJsonDict(jsonDict=json_dict)
            logging.info("Case in models reports 5.0.0")

        if PayloadValidation(klass=InterpretedGenomeRD_4_0_0, payload=json_dict).is_valid:
            ig_v400 = InterpretedGenomeRD_4_0_0.fromJsonDict(jsonDict=json_dict)
            ig_v500 = MigrateReports400To500().migrate_interpreted_genome_rd(
                old_instance=ig_v400, assembly=assembly, interpretation_request_version=interpretation_request_version
            )
            logging.info("Case in models reports 4.0.0")

        elif PayloadValidation(klass=InterpretedGenomeRD_3_0_0, payload=json_dict).is_valid:
            ig_v3 = InterpretedGenomeRD_3_0_0.fromJsonDict(jsonDict=json_dict)
            ig_v400 = MigrateReports3To4().migrate_interpreted_genome_rd(old_instance=ig_v3)
            ig_v500 = MigrateReports400To500().migrate_interpreted_genome_rd(
                old_instance=ig_v400, assembly=assembly, interpretation_request_version=interpretation_request_version
            )
            logging.info("Case in models reports 3.0.0")

        elif PayloadValidation(klass=InterpretedGenomeRD_2_1_0, payload=json_dict).is_valid:
            ig_v2 = InterpretedGenomeRD_2_1_0.fromJsonDict(jsonDict=json_dict)
            ig_v3 = Migration2_1To3().migrate_interpreted_genome(interpreted_genome=ig_v2)
            ig_v400 = MigrateReports3To4().migrate_interpreted_genome_rd(old_instance=ig_v3)
            ig_v500 = MigrateReports400To500().migrate_interpreted_genome_rd(
                old_instance=ig_v400, assembly=assembly, interpretation_request_version=interpretation_request_version
            )
            logging.info("Case in models reports 2.1.0")

        if ig_v500 is not None:
            return ig_v500

        raise MigrationError("Interpreted Genome RD is not in versions: [2.1.0, 3.0.0, 4.2.0]")

    @staticmethod
    def migrate_clinical_report_rd_to_latest(json_dict, assembly):
        """
        :type json_dict: dict
        :type assembly: Assembly
        :rtype: ClinicalReportRD_5_0_0
        """
        cr_v500 = None

        if PayloadValidation(klass=ClinicalReportRD_5_0_0, payload=json_dict).is_valid:
            cr_v500 = ClinicalReportRD_5_0_0.fromJsonDict(jsonDict=json_dict)
            logging.info("Case in models reports 5.0.0")

        elif PayloadValidation(klass=ClinicalReportRD_4_0_0, payload=json_dict).is_valid:
            cr_v4 = ClinicalReportRD_4_0_0.fromJsonDict(jsonDict=json_dict)
            cr_v500 = MigrateReports400To500().migrate_clinical_report_rd(
                old_instance=cr_v4, assembly=assembly
            )
            logging.info("Case in models reports 4.0.0")

        elif PayloadValidation(klass=ClinicalReportRD_3_0_0, payload=json_dict).is_valid:
            cr_v3 = ClinicalReportRD_3_0_0.fromJsonDict(jsonDict=json_dict)
            cr_v4 = MigrateReports3To4().migrate_clinical_report_rd(
                old_clinical_report_rd=cr_v3
            )
            cr_v500 = MigrateReports400To500().migrate_clinical_report_rd(
                old_instance=cr_v4, assembly=assembly
            )
            logging.info("Case in models reports 3.0.0")

        elif PayloadValidation(klass=ClinicalReportRD_2_1_0, payload=json_dict).is_valid:
            cr_v2 = ClinicalReportRD_2_1_0.fromJsonDict(jsonDict=json_dict)
            cr_v3 = Migration2_1To3().migrate_clinical_report(clinical_report=cr_v2)
            cr_v4 = MigrateReports3To4().migrate_clinical_report_rd(
                old_clinical_report_rd=cr_v3
            )
            cr_v500 = MigrateReports400To500().migrate_clinical_report_rd(
                old_instance=cr_v4, assembly=assembly
            )
            logging.info("Case in models reports 2.1.0")

        if cr_v500 is not None:
            return cr_v500

        raise MigrationError("Clinical Report RD is not in versions: [2.1.0, 3.0.0, 4.0.0, 5.0.0]")

    @staticmethod
    def migrate_exit_questionnaire_rd_to_latest(json_dict):
        """
        There are no changes in exit questionnaires between versions 4 and 5
        :type json_dict: dict
        :rtype: RareDiseaseExitQuestionnaire_5_0_0
        """
        eq_v500 = None

        if PayloadValidation(klass=RareDiseaseExitQuestionnaire_5_0_0, payload=json_dict).is_valid:
            eq_v500 = RareDiseaseExitQuestionnaire_5_0_0.fromJsonDict(jsonDict=json_dict)
            logging.info("Exit questionnaire in models reports 5.0.0 or 4.0.0")
        elif PayloadValidation(klass=RareDiseaseExitQuestionnaire_3_0_0, payload=json_dict).is_valid:
            eq_v300 = RareDiseaseExitQuestionnaire_3_0_0.fromJsonDict(jsonDict=json_dict)
            eq_v500 = MigrateReports3To4().migrate_rd_exit_questionnaire(eq_v300)
            logging.info("Exit questionnaire in models reports 3.0.0")

        if eq_v500 is not None:
            return eq_v500

        raise MigrationError("exit Questionnaire RD is not in versions: [3.0.0, 4.0.0, 5.0.0]")

    @staticmethod
    def migrate_pedigree_to_latest(json_dict):
        """
        :type json_dict: dict
        :rtype: Pedigree_1_1_0
        """
        ped_v110 = None

        if PayloadValidation(klass=Pedigree_1_1_0, payload=json_dict).is_valid:
            ped_v110 = Pedigree_1_1_0.fromJsonDict(jsonDict=json_dict)
            logging.info("Pedigree in models participants 1.1.0")

        if PayloadValidation(klass=Pedigree_1_0_3, payload=json_dict).is_valid:
            ped_v103 = Pedigree_1_0_3.fromJsonDict(jsonDict=json_dict)
            ped_v110 = MigrationParticipants103To110().migrate_pedigree(ped_v103)
            logging.info("Pedigree in models participants 1.0.3")

        elif PayloadValidation(klass=Pedigree_1_0_0, payload=json_dict).is_valid:
            ped_v100 = Pedigree_1_0_0.fromJsonDict(jsonDict=json_dict)
            ped_v103 = MigrationParticipants100To103().migrate_pedigree(ped_v100)
            ped_v110 = MigrationParticipants103To110().migrate_pedigree(ped_v103)
            logging.info("Pedigree in models participants 1.0.0")

        elif PayloadValidation(klass=Pedigree_reports_3_0_0, payload=json_dict).is_valid:
            ped_v300 = Pedigree_reports_3_0_0.fromJsonDict(jsonDict=json_dict)
            ped_v100 = MigrationReportsToParticipants1().migrate_pedigree(ped_v300)
            ped_v103 = MigrationParticipants100To103().migrate_pedigree(ped_v100)
            ped_v110 = MigrationParticipants103To110().migrate_pedigree(ped_v103)
            logging.info("Pedigree in models reports 3.1.0")

        if ped_v110 is not None:
            return ped_v110

        raise MigrationError("Pedigree is not in versions: [1.1.0, 1.0.3, 1.0.0, reports 2.1.0]")

    @staticmethod
    def migrate_interpretation_request_cancer_to_latest(json_dict, assembly):
        """
        :type json_dict: dict
        :type assembly: Assembly
        :rtype: CancerInterpretationRequest_5_0_0
        """
        ir_v500 = None

        if PayloadValidation(klass=CancerInterpretationRequest_5_0_0, payload=json_dict).is_valid:
            ir_v500 = CancerInterpretationRequest_5_0_0.fromJsonDict(jsonDict=json_dict)
            logging.info("Cancer interpretation request in models reports 5.0.0")

        elif PayloadValidation(klass=CancerInterpretationRequest_4_0_0, payload=json_dict).is_valid:
            ir_v400 = CancerInterpretationRequest_4_0_0.fromJsonDict(jsonDict=json_dict)
            ir_v500 = MigrateReports400To500().migrate_cancer_interpretation_request(old_instance=ir_v400,
                                                                                     assembly=assembly)
            logging.info("Cancer interpretation request in models reports 4.0.0")

        elif PayloadValidation(klass=CancerInterpretationRequest_3_0_0, payload=json_dict).is_valid:
            ir_v300 = CancerInterpretationRequest_3_0_0.fromJsonDict(jsonDict=json_dict)
            ir_v400 = MigrateReports3To4().migrate_cancer_interpretation_request(old_interpretation_request=ir_v300)
            ir_v500 = MigrateReports400To500().migrate_cancer_interpretation_request(old_instance=ir_v400,
                                                                                     assembly=assembly)
            logging.info("Cancer interpretation request in models reports 3.0.0")

        if ir_v500 is not None:
            return ir_v500

        raise MigrationError("Cancer interpretation request is not in versions: [3.0.0, 4.0.0, 5.0.0]")

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
        ig_v500 = None

        if PayloadValidation(klass=CancerInterpretationRequest_5_0_0, payload=json_dict).is_valid:
            raise MigrationError(
                "Cannot transform a cancer interpretation request in version 5.0.0 into an interpreted genome")

        elif PayloadValidation(klass=CancerInterpretationRequest_4_0_0, payload=json_dict).is_valid:
            ir_v400 = CancerInterpretationRequest_4_0_0.fromJsonDict(jsonDict=json_dict)
            ig_v500 = MigrateReports400To500().migrate_cancer_interpretation_request_to_cancer_interpreted_genome(
                old_instance=ir_v400, assembly=assembly, interpretation_service=interpretation_service,
                reference_database_versions=reference_database_versions, software_versions=software_versions,
                report_url=report_url, comments=comments)
            logging.info("Cancer interpretation request in models reports 4.0.0")

        elif PayloadValidation(klass=CancerInterpretationRequest_3_0_0, payload=json_dict).is_valid:
            ir_v300 = CancerInterpretationRequest_3_0_0.fromJsonDict(jsonDict=json_dict)
            ir_v400 = MigrateReports3To4().migrate_cancer_interpretation_request(old_interpretation_request=ir_v300)
            ig_v500 = MigrateReports400To500().migrate_cancer_interpretation_request_to_cancer_interpreted_genome(
                old_instance=ir_v400, assembly=assembly, interpretation_service=interpretation_service,
                reference_database_versions=reference_database_versions, software_versions=software_versions,
                report_url=report_url, comments=comments)
            logging.info("Cancer interpretation request in models reports 3.0.0")

        if ig_v500 is not None:
            return ig_v500

        raise MigrationError("Cancer interpretation request is not in versions: [3.0.0, 4.0.0]")

    @staticmethod
    def migrate_interpreted_genome_cancer_to_latest(json_dict, assembly=None, participant_id=None,
                                                    sample_id=None, interpretation_request_version=None,
                                                    interpretation_service=None):
        """
        Migration from reports 3.0.0 is not supported as we ave no data in that version
        :type json_dict: dict
        :type assembly: Assembly
        :type participant_id: str
        :type sample_id: str
        :type interpretation_request_version: str
        :type interpretation_service: str
        :rtype: CancerInterpretedGenome_5_0_0
        """
        ig_v500 = None

        if PayloadValidation(klass=CancerInterpretedGenome_5_0_0, payload=json_dict).is_valid:
            ig_v500 = CancerInterpretedGenome_5_0_0.fromJsonDict(jsonDict=json_dict)
            logging.info("Cancer interpreted genome in models reports 5.0.0")

        elif PayloadValidation(klass=CancerInterpretedGenome_4_0_0, payload=json_dict).is_valid:
            if not assembly or not participant_id or not sample_id or not interpretation_request_version \
                    or not interpretation_service:
                raise MigrationError(
                    "Missing required fields to migrate a cancer interpreted genome from 4.0.0 to 5.0.0")
            ig_v400 = CancerInterpretedGenome_4_0_0.fromJsonDict(jsonDict=json_dict)
            ig_v500 = MigrateReports400To500().migrate_cancer_interpreted_genome(
                old_instance=ig_v400, assembly=assembly, participant_id=participant_id, sample_id=sample_id,
                interpretation_request_version=interpretation_request_version,
                interpretation_service=interpretation_service
            )
            logging.info("Cancer interpreted genome in models reports 4.0.0")

        if ig_v500 is not None:
            return ig_v500

        raise MigrationError("Cancer interpreted genome is not in versions: [4.0.0, 5.0.0]")

    @staticmethod
    def migrate_clinical_report_cancer_to_latest(json_dict, sample_id=None, assembly=None, participant_id=None):
        """
        Migration from reports 3.0.0 is not supported as we have no data in that version
        :type json_dict: dict
        :type sample_id: str
        :type assembly: Assembly
        :type participant_id: str
        :rtype: ClinicalReportCancer_5_0_0
        """
        cr_v500 = None

        if PayloadValidation(klass=ClinicalReportCancer_5_0_0, payload=json_dict).is_valid:
            cr_v500 = ClinicalReportCancer_5_0_0.fromJsonDict(jsonDict=json_dict)
            logging.info("Cancer clinical report in models reports 5.0.0")

        elif PayloadValidation(klass=ClinicalReportCancer_4_0_0, payload=json_dict).is_valid:
            if not sample_id or not assembly or not participant_id:
                raise MigrationError("Missing required fields to migrate cancer clinical report from 4.0.0 to 5.0.0")
            cr_v4 = ClinicalReportCancer_4_0_0.fromJsonDict(jsonDict=json_dict)
            cr_v500 = MigrateReports400To500().migrate_cancer_clinical_report(
                old_instance=cr_v4, assembly=assembly, participant_id=participant_id, sample_id=sample_id
            )
            logging.info("Cancer clinical report in models reports 4.0.0")

        if cr_v500 is not None:
            return cr_v500

        raise MigrationError("Cancer clinical report is not in versions: [4.0.0, 5.0.0]")

    @staticmethod
    def migrate_cancer_participant_to_latest(json_dict):
        """
        :type json_dict: dict
        :rtype: CancerParticipant_1_1_0
        """
        cp_v110 = None

        if PayloadValidation(klass=CancerParticipant_1_1_0, payload=json_dict).is_valid:
            cp_v110 = CancerParticipant_1_1_0.fromJsonDict(jsonDict=json_dict)
            logging.info("CancerParticipant in models participants 1.1.0")

        if PayloadValidation(klass=CancerParticipant_1_0_3, payload=json_dict).is_valid:
            cp_v103 = CancerParticipant_1_0_3.fromJsonDict(jsonDict=json_dict)
            cp_v110 = MigrationParticipants103To110().migrate_cancer_participant(cp_v103)
            logging.info("CancerParticipant in models participants 1.0.3")

        elif PayloadValidation(klass=CancerParticipant_1_0_0, payload=json_dict).is_valid:
            cp_v100 = CancerParticipant_1_0_0.fromJsonDict(jsonDict=json_dict)
            cp_v103 = MigrationParticipants100To103().migrate_cancer_participant(cp_v100)
            cp_v110 = MigrationParticipants103To110().migrate_cancer_participant(cp_v103)
            logging.info("CancerParticipant in models participants 1.0.0")

        elif PayloadValidation(klass=CancerParticipant_reports_3_0_0, payload=json_dict).is_valid:
            raise NotImplemented
            # cp_v300 = CancerParticipant_reports_3_0_0.fromJsonDict(jsonDict=json_dict)
            # cp_v100 = MigrationReportsToParticipants1().cuaucuacua(cp_v300)
            # cp_v103 = MigrationParticipants100To103().migrate_cancer_participant(cp_v100)
            # cp_v110 = MigrationParticipants103To110().migrate_cancer_participant(cp_v103)
            # logging.info("CancerParticipant in models reports 3.1.0")

        if cp_v110 is not None:
            return cp_v110

        raise MigrationError("Pedigree is not in versions: [1.1.0, 1.0.3, 1.0.0, reports 2.1.0]")

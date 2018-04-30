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

from protocols.reports_4_0_0 import ClinicalReportCancer as ClinicalReportCancer_4_0_0
from protocols.reports_4_0_0 import ClinicalReportRD as ClinicalReportRD_4_0_0
from protocols.reports_4_0_0 import InterpretationRequestRD as InterpretationRequestRD_4_0_0
from protocols.reports_4_0_0 import InterpretedGenomeRD as InterpretedGenomeRD_4_0_0
from protocols.reports_4_0_0 import CancerInterpretedGenome as CancerInterpretedGenome_4_0_0
from protocols.reports_4_0_0 import CancerInterpretationRequest as CancerInterpretationRequest_4_0_0

from protocols.reports_5_0_0 import Assembly as Assembly_5_0_0
from protocols.reports_5_0_0 import ClinicalReportRD as ClinicalReportRD_5_0_0
from protocols.reports_5_0_0 import InterpretedGenomeRD as InterpretedGenomeRD_5_0_0
from protocols.reports_5_0_0 import ClinicalReportCancer as ClinicalReportCancer_5_0_0
from protocols.reports_5_0_0 import InterpretationRequestRD as InterpretationRequestRD_5_0_0
from protocols.reports_5_0_0 import CancerInterpretedGenome as CancerInterpretedGenome_5_0_0
from protocols.reports_5_0_0 import CancerInterpretationRequest as CancerInterpretationRequest_5_0_0

from protocols.participant_1_0_3 import Pedigree as Pedigree_1_0_3
from protocols.participant_1_0_0 import Pedigree as Pedigree_1_0_0
from protocols.reports_3_0_0 import Pedigree as Pedigree_reports_3_0_0

from protocols.migration.model_validator import PayloadValidation
from protocols.migration.migration import Migration2_1To3
from protocols.migration.migration_reports_3_0_0_to_reports_4_0_0 import \
    MigrationReportsToParticipants1, MigrateReports3To4
from protocols.migration.migration_reports_4_0_0_to_reports_5_0_0 import MigrateReports400To500
from protocols.migration.participants import MigrationParticipants1ToReports, MigrationParticipants100To103


def migrate_interpretation_request_rd_to_version_5_0_0(json_dict, assembly):
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


def migrate_interpreted_genome_rd_to_version_5_0_0(json_dict, assembly, interpretation_request_version):
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


def migrate_clinical_report_rd_to_version_5_0_0(json_dict, assembly):
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


def migrate_pedigree_to_version_1_0_3(json_dict):
    ped_v103 = None

    if PayloadValidation(klass=Pedigree_1_0_3, payload=json_dict).is_valid:
        ped_v103 = Pedigree_1_0_3.fromJsonDict(jsonDict=json_dict)
        logging.info("Pedigree in models participants 1.0.3")

    elif PayloadValidation(klass=Pedigree_1_0_0, payload=json_dict).is_valid:
        ped_v100 = Pedigree_1_0_0.fromJsonDict(jsonDict=json_dict)
        ped_v103 = MigrationParticipants100To103().migrate_pedigree(old_pedigree=ped_v100)
        logging.info("Pedigree in models participants 1.0.0")

    elif PayloadValidation(klass=Pedigree_reports_3_0_0, payload=json_dict).is_valid:
        ped_v300 = Pedigree_reports_3_0_0.fromJsonDict(jsonDict=json_dict)
        ped_v100 = MigrationReportsToParticipants1().migrate_pedigree(pedigree=ped_v300)
        ped_v103 = MigrationParticipants100To103().migrate_pedigree(old_pedigree=ped_v100)
        logging.info("Pedigree in models reports 3.1.0")

    if ped_v103 is not None:
        return ped_v103

    raise MigrationError("Pedigree is not in versions: [1.0.3, 1.0.0, reports 2.1.0]")

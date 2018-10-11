from protocols import reports_4_0_0, reports_5_0_0, reports_6_0_0
from protocols.migration import MigrationHelpers, MigrateReports600To500, Migration21To3
from protocols.tests.test_migration.base_test_migration import BaseRoundTripper


class MigrationRunner(BaseRoundTripper):

    def roundtrip_rd_ir(self, ir, assembly):
        ig6 = MigrationHelpers.migrate_interpretation_request_rd_to_interpreted_genome_latest(
            ir.toJsonDict(), assembly=assembly)
        ig5 = MigrateReports600To500().migrate_interpreted_genome_to_interpreted_genome_rd(ig6)
        migrated, round_tripped = self.round_trip_migration(
            MigrationHelpers.migrate_interpretation_request_rd_to_latest,
            MigrationHelpers.reverse_migrate_interpretation_request_rd_to_v3,
            ir,
            forward_kwargs={'assembly': assembly},
            backward_kwargs={'ig_json_dict': ig5.toJsonDict()})
        return migrated, round_tripped

    def roundtrip_rd_ig(self, ig, assembly):
        migrated, round_tripped = self.round_trip_migration(
            MigrationHelpers.migrate_interpreted_genome_rd_to_latest,
            MigrationHelpers.reverse_migrate_interpreted_genome_rd_to_v3,
            ig,
            forward_kwargs={'assembly': assembly, 'interpretation_request_version': 1})
        return migrated, round_tripped

    def roundtrip_rd_cr(self, cr, assembly):
        migrated, round_tripped = self.round_trip_migration(
            MigrationHelpers.migrate_clinical_report_rd_to_latest,
            MigrationHelpers.reverse_migrate_clinical_report_rd_to_v3,
            cr, forward_kwargs={'assembly': assembly})
        return migrated, round_tripped

    def roundtrip_rd_eq(self, eq, assembly):
        migrated, round_tripped = self.round_trip_migration(
            MigrationHelpers.migrate_exit_questionnaire_rd_to_latest,
            MigrationHelpers.reverse_migrate_exit_questionnaire_rd_to_v3,
            eq, forward_kwargs={'assembly': assembly})
        return migrated, round_tripped

    def roundtrip_cancer_ir(self, ir, assembly):
        """
        :type ir: reports_4_0_0.CancerInterpretationRequest
        :type assembly: reports_4_0_0.Assembly
        :rtype: (reports_6_0_0.CancerInterpretationRequest, reports_4_0_0.CancerInterpretationRequest)
        """
        ig6 = MigrationHelpers.migrate_interpretation_request_cancer_to_interpreted_genome_latest(
            ir.toJsonDict(), assembly=assembly, interpretation_service="service",
            reference_database_versions={}, software_versions={}, report_url="https://example.com", comments=[])
        migrated, round_tripped = self.round_trip_migration(
            MigrationHelpers.migrate_interpretation_request_cancer_to_latest,
            MigrationHelpers.reverse_migrate_interpretation_request_cancer_to_v4,
            ir,
            forward_kwargs={'assembly': assembly},
            backward_kwargs={'ig_json_dict': ig6.toJsonDict()})
        return migrated, round_tripped

    def roundtrip_cancer_ig(self, ig, assembly):
        """
        :type ig: reports_4_0_0.CancerInterpretedGenome
        :type assembly: reports_4_0_0.Assembly
        :rtype: (reports_6_0_0.InterpretedGenome, reports_4_0_0.CancerInterpretedGenome)
        """
        migrated, round_tripped = self.round_trip_migration(
            MigrationHelpers.migrate_interpreted_genome_cancer_to_latest,
            MigrationHelpers.reverse_migrate_interpreted_genome_cancer_to_v4,
            ig,
            forward_kwargs={'assembly': assembly, 'participant_id': '1',
                            'sample_ids': {'somatic_variant': 'somatic1', 'germline_variant': 'germline1'},
                            'interpretation_request_version': 1, 'interpretation_service': '1'}
        )
        return migrated, round_tripped

    def roundtrip_cancer_cr(self, cr, assembly):
        """
        :type cr: reports_4_0_0.ClinicalReportCancer
        :type assembly: reports_4_0_0.Assembly
        :rtype: (reports_6_0_0.ClinicalReport, reports_4_0_0.CancerClinicalReport)
        """
        migrated, round_tripped = self.round_trip_migration(
            MigrationHelpers.migrate_clinical_report_cancer_to_latest,
            MigrationHelpers.reverse_migrate_clinical_report_cancer_to_v4,
            cr, forward_kwargs={'assembly': assembly, 'participant_id': '1',
                                'sample_ids': {'somatic_variant': 'somatic1',
                                               'germline_variant': 'germline1'}
                                }
        )
        return migrated, round_tripped

    def roundtrip_cancer_eq(self, eq, assembly):
        """
        :type eq: reports_5_0_0.CancerExitQuestionnaire
        :type assembly: reports_5_0_0.Assembly
        :rtype: (reports_6_0_0.CancerExitQuestionnaire, reports_4_0_0.CancerExitQuestionnaire)
        """
        migrated, round_tripped = self.round_trip_migration(
            MigrationHelpers.migrate_cancer_exit_questionnaire_to_latest,
            MigrationHelpers.reverse_migrate_cancer_exit_questionnaire_to_v5,
            eq, forward_kwargs={'assembly': assembly}
        )
        return migrated, round_tripped

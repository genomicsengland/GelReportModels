from protocols import reports_4_0_0, reports_5_0_0, reports_6_0_0
from protocols.migration import MigrationHelpers
from protocols.tests.test_migration.base_test_migration import BaseRoundTripper


class MigrationRunner(BaseRoundTripper):

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
            forward_kwargs={'assembly': assembly, 'participant_id': '1', 'sample_id': '1',
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
            cr, forward_kwargs={'assembly': assembly, 'participant_id': '1', 'sample_id': '1'}
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

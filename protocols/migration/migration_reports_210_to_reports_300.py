import logging
from protocols import reports_2_1_0, reports_3_0_0 as reports_3_0_0
from protocols.migration.base_migration import BaseMigration, MigrationError


class Migration21To3(BaseMigration):

    new_model = reports_3_0_0
    old_model = reports_2_1_0

    def migrate_interpreted_genome(self, interpreted_genome):
        """
        :type interpreted_genome: reports_2_1_0.InterpretedGenomeRD
        :rtype: reports_3_0_0.InterpretedGenomeRD
        """
        new_instance = self.convert_class(self.new_model.InterpretedGenomeRD, interpreted_genome)
        new_instance.reportedVariants = self.convert_collection(
            interpreted_genome.reportedVariants, self._migrate_reported_variant)
        new_instance.reportedStructuralVariants = []
        interpreted_genome.versionControl = reports_3_0_0.VersionControl()
        new_instance.softwareVersions = {}
        new_instance.referenceDatabasesVersions = {}
        return self.validate_object(new_instance, self.new_model.InterpretedGenomeRD)

    def migrate_interpretation_request(self, interpretation_request):
        """
        :type interpretation_request: reports_2_1_0.InterpretationRequestRD
        :rtype: reports_3_0_0.InterpretationRequestRD
        """
        new_instance = self.convert_class(self.new_model.InterpretationRequestRD, interpretation_request)
        new_instance.pedigree = self.migrate_pedigree(interpretation_request.pedigree)
        new_instance.versionControl = reports_3_0_0.VersionControl()
        new_instance.TieredVariants = self.convert_collection(
            interpretation_request.TieredVariants, self._migrate_reported_variant)
        return self.validate_object(new_instance, self.new_model.InterpretationRequestRD)

    def migrate_clinical_report(self, clinical_report):
        """
        :type clinical_report: reports_2_1_0.ClinicalReportRD
        :rtype: reports_3_0_0.ClinicalReportRD
        """
        new_instance = self.convert_class(self.new_model.ClinicalReportRD, clinical_report)
        new_instance.candidateVariants = self.convert_collection(
            clinical_report.candidateVariants, self._migrate_reported_variant)
        new_instance.candidateStructuralVariants = []
        return self.validate_object(new_instance, self.new_model.ClinicalReportRD)

    def migrate_pedigree(self, pedigree):
        """
        :type pedigree: reports_2_1_0.Pedigree
        :rtype: reports_3_0_0.Pedigree
        """
        new_instance = self.convert_class(self.new_model.Pedigree, pedigree)
        new_instance.versionControl = reports_3_0_0.VersionControl()
        new_instance.participants = self.convert_collection(pedigree.participants, self._migrate_rd_participant)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Pedigree)

    def _migrate_rd_participant(self, member):
        new_instance = self.convert_class(self.new_model.RDParticipant, member)
        new_instance.versionControl = reports_3_0_0.VersionControl()
        if member.additionalInformation:
            if 'yearOfBirth' in member.additionalInformation:
                new_instance.yearOfBirth = member.additionalInformation['yearOfBirth']
        return new_instance

    def _migrate_reported_called_genotype(self, called_genotype):
        new_instance = self.convert_class(self.new_model.CalledGenotype, called_genotype)
        if new_instance.validate(new_instance.toJsonDict()):
            return new_instance
        else:
            logging.warning("Lost genotype '{}' during migration".format(called_genotype.genotype))
            new_instance.genotype = 'unk'
        return new_instance

    def _migrate_genomic_feature(self, genomic_feature):
        new_instance = self.convert_class(self.new_model.GenomicFeature, genomic_feature)
        if genomic_feature.ids and 'HGNC' in genomic_feature.ids:
            new_instance.HGNC = genomic_feature.ids['HGNC']
        new_instance.other_ids = genomic_feature.ids
        return new_instance

    def _migrate_report_event(self, report_event):
        new_instance = self.convert_class(self.new_model.ReportEvent, report_event)
        new_instance.genomicFeature = self._migrate_genomic_feature(report_event.genomicFeature)
        return new_instance

    def _migrate_reported_variant(self, reported_variant):
        new_instance = self.convert_class(self.new_model.ReportedVariant, reported_variant)
        new_instance.calledGenotypes = self.convert_collection(
            reported_variant.calledGenotypes, self._migrate_reported_called_genotype)
        new_instance.reportEvents = self.convert_collection(reported_variant.reportEvents, self._migrate_report_event)
        return new_instance

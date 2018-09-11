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
            list(zip(interpreted_genome.reportedVariants, new_instance.reportedVariants)), self._migrate_reported_variant)
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
            list(zip(interpretation_request.TieredVariants, new_instance.TieredVariants)), self._migrate_reported_variant)
        new_instance.BAMs = self.convert_collection(list(zip(interpretation_request.BAMs, new_instance.BAMs)), self._migrate_file)
        new_instance.VCFs = self.convert_collection(list(zip(interpretation_request.VCFs, new_instance.VCFs)), self._migrate_file)
        if interpretation_request.bigWigs is not None:
            new_instance.bigWigs = self.convert_collection(
                list(zip(interpretation_request.bigWigs, new_instance.bigWigs)), self._migrate_file)
        if interpretation_request.pedigreeDiagram:
            new_instance.pedigreeDiagram = self._migrate_file(
                (interpretation_request.pedigreeDiagram, new_instance.pedigreeDiagram))
        if interpretation_request.annotationFile:
            new_instance.annotationFile = self._migrate_file(
                (interpretation_request.annotationFile, new_instance.annotationFile))
        return self.validate_object(new_instance, self.new_model.InterpretationRequestRD)

    def migrate_clinical_report(self, clinical_report):
        """
        :type clinical_report: reports_2_1_0.ClinicalReportRD
        :rtype: reports_3_0_0.ClinicalReportRD
        """
        new_instance = self.convert_class(self.new_model.ClinicalReportRD, clinical_report)
        new_instance.candidateVariants = self.convert_collection(
            list(zip(clinical_report.candidateVariants, new_instance.candidateVariants)), self._migrate_reported_variant)
        new_instance.candidateStructuralVariants = []
        return self.validate_object(new_instance, self.new_model.ClinicalReportRD)

    def migrate_pedigree(self, pedigree):
        """
        :type pedigree: reports_2_1_0.Pedigree
        :rtype: reports_3_0_0.Pedigree
        """
        new_instance = self.convert_class(self.new_model.Pedigree, pedigree)
        new_instance.versionControl = reports_3_0_0.VersionControl()
        new_instance.participants = self.convert_collection(
            list(zip(pedigree.participants, new_instance.participants)), self._migrate_rd_participant)
        return self.validate_object(object_to_validate=new_instance, object_type=self.new_model.Pedigree)

    def _migrate_file(self, files):
        old_instance = files[0]
        new_instance = files[1]
        if old_instance.fileType == self.old_model.FileType.TIER:
            return None
        return new_instance

    def _migrate_rd_participant(self, members):
        old_instance = members[0]
        new_instance = members[1]
        new_instance.versionControl = reports_3_0_0.VersionControl()
        if old_instance.additionalInformation:
            if 'yearOfBirth' in old_instance.additionalInformation:
                new_instance.yearOfBirth = old_instance.additionalInformation['yearOfBirth']
        return new_instance

    def _migrate_reported_called_genotype(self, called_genotypes):
        old_instance = called_genotypes[0]
        new_instance = called_genotypes[1]
        if new_instance.validate(new_instance.toJsonDict()):
            return new_instance
        else:
            logging.warning("Lost genotype '{}' during migration".format(old_instance.genotype))
            new_instance.genotype = 'unk'
        return new_instance

    def _migrate_genomic_feature(self, old_instance, new_instance):
        if old_instance.ids and 'HGNC' in old_instance.ids:
            new_instance.HGNC = old_instance.ids['HGNC']
        new_instance.other_ids = old_instance.ids
        return new_instance

    def _migrate_report_event(self, report_events):
        old_instance = report_events[0]
        new_instance = report_events[1]
        new_instance.genomicFeature = self._migrate_genomic_feature(old_instance.genomicFeature, new_instance.genomicFeature)
        return new_instance

    def _migrate_reported_variant(self, reported_variants):
        old_instance = reported_variants[0]
        new_instance = reported_variants[1]
        new_instance.calledGenotypes = self.convert_collection(
            list(zip(old_instance.calledGenotypes, new_instance.calledGenotypes)), self._migrate_reported_called_genotype)
        new_instance.reportEvents = self.convert_collection(
            list(zip(old_instance.reportEvents, new_instance.reportEvents)), self._migrate_report_event)
        return new_instance

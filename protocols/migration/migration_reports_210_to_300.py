import logging
from protocols import reports_2_1_0, reports_3_0_0 as reports_3_0_0
from protocols.migration.base_migration import BaseMigration


class Migration2_1To3(BaseMigration):
    new_model = reports_3_0_0
    old_model = reports_2_1_0

    def migrate_pedigree(self, pedigree):
        """

        :type pedigree: reports_2_1_0.Pedigree
        :rtype: reports_3_0_0.Pedigree
        """

        new_pedigree = self.new_model.Pedigree()

        new_pedigree.analysisPanels = pedigree.analysisPanels
        new_pedigree.diseasePenetrances = None
        new_pedigree.versionControl = reports_3_0_0.VersionControl()
        new_pedigree.gelFamilyId = pedigree.gelFamilyId
        if pedigree.participants is not None:
            new_pedigree.participants = [self.migrate_rd_participant(member) for member in pedigree.participants]

        if new_pedigree.validate(new_pedigree.toJsonDict()):
            return new_pedigree
        else:
            raise Exception('This model can not be converted')

    def migrate_rd_participant(self, member):
        """

        :type member: reports_2_1_0.RDParticipant
        :rtype: reports_3_0_0.RDParticipant
        """
        new_rd_participant = self.convert_class(self.new_model.RDParticipant, member)
        new_rd_participant.versionControl = reports_3_0_0.VersionControl()
        if member.additionalInformation:
            if 'yearOfBirth' in member.additionalInformation:
                new_rd_participant.yearOfBirth = member.additionalInformation['yearOfBirth']

        if new_rd_participant.validate(new_rd_participant.toJsonDict()):
            return new_rd_participant
        else:
            raise Exception('This model can not be converted')

    def migrate_reported_called_genotype(self, called_genotype):
        """

        :rtype: reports_3_0_0.CalledGenotype
        :type called_genotype: reports_2_1_0.CalledGenotype
        """

        new_called_genotype = self.convert_class(self.new_model.CalledGenotype, called_genotype)
        if new_called_genotype.validate(new_called_genotype.toJsonDict()):
            return new_called_genotype
        else:
            logging.warning("Lost genotype '{}' during migration".format(called_genotype.genotype))
            new_called_genotype.genotype = 'unk'
            if new_called_genotype.validate(new_called_genotype.toJsonDict(), verbose=True):
                return new_called_genotype
            else:
                raise Exception('This model can not be converted')

    def migrate_genomic_feature(self, genomic_feature):
        """

        :type genomic_feature: reports_2_1_0.GenomicFeature
        :rtype: reports_3_0_0.GenomicFeature
        """

        new_genomic_feature = self.new_model.GenomicFeature()
        new_genomic_feature.featureType = genomic_feature.featureType
        new_genomic_feature.ensemblId = genomic_feature.ensemblId
        if genomic_feature.ids and 'HGNC' in genomic_feature.ids:
            new_genomic_feature.HGNC = genomic_feature.ids['HGNC']
        new_genomic_feature.other_ids = genomic_feature.ids

        if new_genomic_feature.validate(new_genomic_feature.toJsonDict()):
            return new_genomic_feature
        else:
            raise Exception('This model can not be converted')

    def migrate_report_event(self, report_event):
        """

        :type report_event: reports_2_1_0.ReportEvent
        :rtype: reports_3_0_0.ReportEvent
        """

        new_report_event = self.convert_class(self.new_model.ReportEvent, report_event)
        new_report_event.genomicFeature = self.migrate_genomic_feature(report_event.genomicFeature)

        if new_report_event.validate(new_report_event.toJsonDict()):
            return new_report_event
        else:
            raise Exception('This model can not be converted')

    def migrate_reported_variant(self, reported_variant):
        """

        :type reported_variant: reports_2_1_0.ReportedVariant
        :rtype: reports_3_0_0.ReportedVariant
        """

        new_reported_variant = self.convert_class(self.new_model.ReportedVariant, reported_variant)

        if reported_variant.calledGenotypes is not None:
            new_reported_variant.calledGenotypes = [
                self.migrate_reported_called_genotype(called_genotype)
                for called_genotype in reported_variant.calledGenotypes
            ]

        if reported_variant.reportEvents is not None:
            new_reported_variant.reportEvents = [self.migrate_report_event(report_event)
                                                 for report_event in reported_variant.reportEvents]

        if new_reported_variant.validate(new_reported_variant.toJsonDict()):
            return new_reported_variant
        else:
            raise Exception('This model can not be converted')

    def migrate_reported_structural_variant(self, reported_structural_variant):
        """

        :type reported_structural_variant: reports_2_1_0.ReportedStructuralVariant
        :rtype: reports_3_0_0.ReportedStructuralVariant
        """
        new_reported_structural_variant = self.new_model.ReportedStructuralVariant.fromJsonDict(
            reported_structural_variant.toJsonDict())
        if reported_structural_variant.calledGenotypes is not None:
            new_reported_structural_variant.calledGenotypes = [
                self.migrate_reported_called_genotype(called_genotype)
                for called_genotype in reported_structural_variant.calledGenotypes]
        if reported_structural_variant.reportEvents is not None:
            new_reported_structural_variant.reportEvents = [
                self.migrate_report_event(report_event)
                for report_event in reported_structural_variant.reportEvents]

        if new_reported_structural_variant.validate(new_reported_structural_variant.toJsonDict()):
            return new_reported_structural_variant
        else:
            raise Exception('This model can not be converted')

    def migrate_interpreted_genome(self, interpreted_genome):
        """

        :type interpreted_genome: reports_2_1_0.InterpretedGenomeRD
        :rtype: reports_3_0_0.InterpretedGenomeRD
        """

        new_interpreted_genome = self.convert_class(self.new_model.InterpretedGenomeRD, interpreted_genome)
        if interpreted_genome.reportedVariants is not None:
            new_interpreted_genome.reportedVariants = [
                self.migrate_reported_variant(reported_variant)
                for reported_variant in interpreted_genome.reportedVariants]
        if interpreted_genome.reportedStructuralVariants is not None:
            new_interpreted_genome.reportedStructuralVariants = [
                self.migrate_reported_structural_variant(reported_structural_variant)
                for reported_structural_variant in interpreted_genome.reportedStructuralVariants]
        interpreted_genome.versionControl = reports_3_0_0.VersionControl()
        new_interpreted_genome.softwareVersions = {}
        new_interpreted_genome.referenceDatabasesVersions = {}

        if new_interpreted_genome.validate(new_interpreted_genome.toJsonDict(), verbose=True):
            return new_interpreted_genome
        else:
            raise Exception('This model can not be converted')

    def migrate_interpretation_request(self, interpretation_request):
        """

        :type interpretation_request: reports_2_1_0.InterpretationRequestRD
        :rtype: reports_3_0_0.InterpretationRequestRD
        """

        new_interpretation_request = self.convert_class(self.new_model.InterpretationRequestRD, interpretation_request)
        new_interpretation_request.pedigree = self.migrate_pedigree(interpretation_request.pedigree)
        new_interpretation_request.versionControl = reports_3_0_0.VersionControl()
        if interpretation_request.TieredVariants is not None:
            new_interpretation_request.TieredVariants = [self.migrate_reported_variant(tiered_variant)
                                                         for tiered_variant in interpretation_request.TieredVariants]

        if new_interpretation_request.validate(new_interpretation_request.toJsonDict(), verbose=True):
            return new_interpretation_request
        else:
            raise Exception('This model can not be converted')

    def migrate_clinical_report(self, clinical_report):
        """

        :type clinical_report: reports_2_1_0.ClinicalReportRD
        :rtype: reports_3_0_0.ClinicalReportRD
        """

        new_clinical_report = self.convert_class(self.new_model.ClinicalReportRD, clinical_report)

        if clinical_report.candidateVariants is not None:
            new_clinical_report.candidateVariants = [self.migrate_reported_variant(reported_variant)
                                                     for reported_variant in clinical_report.candidateVariants]

        if clinical_report.candidateStructuralVariants is not None:
            new_clinical_report.candidateStructuralVariants = [
                self.migrate_reported_structural_variant(reported_structural_variant)
                for reported_structural_variant in clinical_report.candidateStructuralVariants
            ]

        if new_clinical_report.validate(new_clinical_report.toJsonDict()):
            return new_clinical_report
        else:
            raise Exception('This model can not be converted')





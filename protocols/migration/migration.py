from protocols import reports_2_1_0, reports_3_0_0 as reports_3_0_0, reports_3_1_0 as reports_3_1_0


class Migration3_0_0To3_1_0(object):
    new_model = reports_3_1_0
    old_model = reports_3_0_0

    def migrate_interpretation_request_rd(self, interpretation_request):
        """

        :type interpretation_request: reports_3_0_0.InterpretationRequestRD
        :rtype: reports_3_1_0.InterpretationRequestRD
        """

        new_interpretation_request = self.new_model.InterpretationRequestRD

        # TODO: implement changes
        new_interpretation_request.versionControl = self.migrate_version_control(interpretation_request.versionControl)
        new_interpretation_request.interpretationRequestId = interpretation_request.InterpretationRequestID
        new_interpretation_request.interpretationRequestVersion = interpretation_request.InterpretationRequestVersion
        new_interpretation_request.bams = [self.migrate_file(bam) for bam in interpretation_request.BAMs]
        new_interpretation_request.vcfs = [self.migrate_file(vcf) for vcf in interpretation_request.VCFs]
        new_interpretation_request.bigWigs = [self.migrate_file(vcf) for vcf in interpretation_request.bigWigs]
        new_interpretation_request.pedigreeDiagram = [self.migrate_file(vcf) for vcf in interpretation_request.pedigreeDiagram]
        new_interpretation_request.annotationFile = [self.migrate_file(vcf) for vcf in interpretation_request.annotationFile]
        #new_ir.analysisPanels = ir.analysisPanels
        #new_ir.diseasePenetrances = None
        #new_ir.versionControl = reports_3_0_0.VersionControl()
        #new_ir.gelFamilyId = ir.gelFamilyId
        #new_ir.participants = []
        #for member in ir.participants:
        #    new_ir.participants.append(self.migrate_rd_participant(member))

        if new_interpretation_request.validate(new_interpretation_request.toJsonDict()):
            return new_interpretation_request
        else:
            raise Exception('This model can not be converted')

    def migrate_interpreted_genome_rd(self, interpreted_genome):
        """

        :type interpreted_genome_rd: reports_3_0_0.InterpretedGenomeRD
        :rtype: reports_3_1_0.InterpretedGenomeRD
        """

        new_interpreted_genome = self.new_model.InterpretedGenomeRD

        # TODO: implement changes
        new_interpreted_genome.versionControl = self.migrate_version_control(interpreted_genome.versionControl)



        if new_interpreted_genome.validate(new_interpreted_genome.toJsonDict()):
            return new_interpreted_genome
        else:
            raise Exception('This model can not be converted')

    def migrate_clinical_report_rd(self, clinical_report):
        """

        :type interpreted_genome_rd: reports_3_0_0.ClinicalReportRD
        :rtype: reports_3_1_0.ClinicalReportRD
        """

        new_clinical_report = self.new_model.ClinicalReportRD

        # TODO: implement changes
        #new_ir.analysisPanels = ir.analysisPanels
        #new_ir.diseasePenetrances = None
        #new_ir.versionControl = reports_3_0_0.VersionControl()
        #new_ir.gelFamilyId = ir.gelFamilyId
        #new_ir.participants = []
        #for member in ir.participants:
        #    new_ir.participants.append(self.migrate_rd_participant(member))

        if new_clinical_report.validate(new_clinical_report.toJsonDict()):
            return new_clinical_report
        else:
            raise Exception('This model can not be converted')

    def migrate_version_control(self, version_control):
        """

        :type version_control: reports_3_0_0.VersionControl
        :rtype: reports_3_1_0.VersionControl
        """
        new_version_control = self.new_model.VersionControl
        # implement changes
        new_version_control.gitVersionControl = version_control.GitVersionControl
        if new_version_control.validate(new_version_control.toJsonDict()):
            return new_version_control
        else:
            raise Exception('This model can not be converted')

    def migrate_file(self, file):
        """

        :type file: reports_3_0_0.File
        :rtype: reports_3_1_0.File
        """
        new_file = self.new_model.File
        # implement changes
        new_file.sampleId = file.SampleId
        new_file.uriFile = file.URIFile
        if new_file.validate(new_file.toJsonDict()):
            return new_file
        else:
            raise Exception('This model can not be converted')



class Migration2_1To3(object):
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
        new_pedigree.participants = []
        for member in pedigree.participants:
            new_pedigree.participants.append(self.migrate_rd_participant(member))

        if new_pedigree.validate(new_pedigree.toJsonDict()):
            return new_pedigree
        else:
            raise Exception('This model can not be converted')

    def migrate_rd_participant(self, member):
        """

        :type member: reports_2_1_0.RDParticipant
        :rtype: reports_3_0_0.RDParticipant
        """
        new_rd_participant = self.new_model.RDParticipant.fromJsonDict(member.toJsonDict())
        new_rd_participant.versionControl = reports_3_0_0.VersionControl()
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

        new_called_genotype = self.new_model.CalledGenotype.fromJsonDict(called_genotype.toJsonDict())
        if new_called_genotype.validate(new_called_genotype.toJsonDict()):
            return new_called_genotype
        else:
            new_called_genotype.genotype = 'unk'
            if new_called_genotype.validate(new_called_genotype.toJsonDict()):
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

        new_report_event = self.new_model.ReportEvent.fromJsonDict(report_event.toJsonDict())
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

        new_reported_variant = self.new_model.ReportedVariant.fromJsonDict(reported_variant.toJsonDict())
        new_reported_variant.calledGenotypes = []
        new_reported_variant.reportEvents = []

        for called_genotype in reported_variant.calledGenotypes:
            new_reported_variant.calledGenotypes.append(self.migrate_reported_called_genotype(called_genotype))

        for report_event in reported_variant.reportEvents:
            new_reported_variant.reportEvents.append(self.migrate_report_event(report_event))

        if new_reported_variant.validate(new_reported_variant.toJsonDict()):
            return new_reported_variant
        else:
            raise Exception('This model can not be converted')

    def migrate_reported_structural_variant(self, reported_structural_variant):
        """

        :type reported_structural_variant: reports_2_1_0.ReportedStructuralVariant
        :rtype: reports_3_0_0.ReportedStructuralVariant
        """

        new_reported_structural_variant = self.new_model.ReportedStructuralVariant.fromJsonDict(reported_structural_variant.toJsonDict())
        new_reported_structural_variant.calledGenotypes = []
        new_reported_structural_variant.reportEvents = []

        for called_genotype in reported_structural_variant.calledGenotypes:
            new_reported_structural_variant.calledGenotypes.append(self.migrate_reported_called_genotype(called_genotype))

        for report_event in reported_structural_variant.reportEvents:
            new_reported_structural_variant.reportEvents.append(self.migrate_report_event(report_event))

        if new_reported_structural_variant.validate(new_reported_structural_variant.toJsonDict()):
            return new_reported_structural_variant
        else:
            raise Exception('This model can not be converted')

    def migrate_interpreted_genome(self, interpreted_genome):
        """

        :type interpreted_genome: reports_2_1_0.InterpretedGenomeRD
        :rtype: reports_3_0_0.InterpretedGenomeRD
        """

        new_interpreted_genome = self.new_model.InterpretedGenomeRD.fromJsonDict(interpreted_genome.toJsonDict())
        new_interpreted_genome.reportedVariants = []
        new_interpreted_genome.ReportedStructuralVariant = []
        interpreted_genome.versionControl = reports_3_0_0.VersionControl()

        for reported_variant in interpreted_genome.reportedVariants:
            new_interpreted_genome.reportedVariants.append(self.migrate_reported_variant(reported_variant))

        if interpreted_genome.reportedStructuralVariants:
            for reported_structural_variant in interpreted_genome.reportedStructuralVariants:
                new_interpreted_genome.ReportedStructuralVariant.append(self.migrate_reported_structural_variant(reported_structural_variant))

        new_interpreted_genome.softwareVersions = {}
        new_interpreted_genome.referenceDatabasesVersions = {}

        if new_interpreted_genome.validate(new_interpreted_genome.toJsonDict()):
            return new_interpreted_genome
        else:
            raise Exception('This model can not be converted')

    def migrate_interpretation_request(self, interpretation_request):
        """

        :type interpretation_request: reports_2_1_0.InterpretationRequestRD
        :rtype: reports_3_0_0.InterpretationRequestRD
        """

        new_interpretation_request = self.new_model.InterpretationRequestRD.fromJsonDict(interpretation_request.toJsonDict())
        new_interpretation_request.TieredVariants = []
        new_interpretation_request.pedigree = self.migrate_pedigree(interpretation_request.pedigree)
        new_interpretation_request.versionControl = reports_3_0_0.VersionControl()
        for tiered_variant in interpretation_request.TieredVariants:
            new_interpretation_request.TieredVariants.append(self.migrate_reported_variant(tiered_variant))

        if new_interpretation_request.validate(new_interpretation_request.toJsonDict()):
            return new_interpretation_request
        else:
            raise Exception('This model can not be converted')

    def migrate_clinical_report(self, clinical_report):
        """

        :type clinical_report: reports_2_1_0.ClinicalReportRD
        :rtype: reports_3_0_0.ClinicalReportRD
        """

        new_clinical_report = self.new_model.ClinicalReportRD.fromJsonDict(clinical_report.toJsonDict())
        new_clinical_report.candidateVariants = []
        new_clinical_report.candidateStructuralVariants = []
        for reported_variant in clinical_report.candidateVariants:
            new_clinical_report.candidateVariants.append(self.migrate_reported_variant(reported_variant))

        if clinical_report.candidateStructuralVariants:
            for reported_structural_variant in clinical_report.candidateStructuralVariants:
                new_clinical_report.candidateStructuralVariants.append(
                    self.migrate_reported_structural_variant(reported_structural_variant))

        if new_clinical_report.validate(new_clinical_report.toJsonDict()):
            return new_clinical_report
        else:
            raise Exception('This model can not be converted')





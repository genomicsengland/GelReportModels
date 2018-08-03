import factory.fuzzy
from protocols.util.dependency_manager import VERSION_300
from protocols.reports_3_0_0 import (
    CancerParticipant,
    CancerSample,
    ReportedVariantCancer,
    ReportEventCancer,
    Actions,
    CancerInterpretationRequest,
    VersionControl,
    CancerDemographics,
    ConsentStatus,
    File,
    MatchedSamples,
    GenomicFeatureCancer,
    ReportedSomaticVariants
)
from protocols.util.factories.avro_factory import FactoryAvro


class CancerSampleFactory(FactoryAvro):
    def __init__(self, *args, **kwargs):
        super(CancerSampleFactory, self).__init__(*args, **kwargs)

    class Meta:
        model = CancerSample

    _version = VERSION_300

    labId = '1'
    preservationMethod = factory.fuzzy.FuzzyChoice(["FF", "FFPE"])
    phase = factory.fuzzy.FuzzyChoice(["PRIMARY"])



class CancerParticipantFactory(FactoryAvro):
    def __init__(self, *args, **kwargs):
        super(CancerParticipantFactory, self).__init__(*args, **kwargs)

    class Meta:
        model = CancerParticipant

    _version = VERSION_300

    versionControl = VersionControl()

    @factory.post_generation
    def cancerSamples(self, create, extacted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if not extacted:
            extacted = [
                CancerSampleFactory.create(sampleType='germline'),
                CancerSampleFactory.create(sampleType='tumor'),
            ]

        # A list of groups were passed in, use them
        for f in extacted:
            self.cancerSamples = []
            if f:
                self.cancerSamples.append(f)
        self.matchedSamples = [MatchedSamples(germlineSampleId=extacted[0].sampleId,
                                              tumorSampleId=extacted[1].sampleId
                                              )]


class ReportEventCancerFactory(FactoryAvro):
    def __init__(self, *args, **kwargs):
        super(ReportEventCancerFactory, self).__init__(*args, **kwargs)

    class Meta:
        model = ReportEventCancer

    _version = VERSION_300

    soTerms = [str(factory.fuzzy.FuzzyText('SO:', length=7).fuzz()) for _ in range(0, 2)]
    soNames = [str(factory.fuzzy.FuzzyText(length=8).fuzz()) for _ in range(0, 2)]


class CancerReportedVariantsFactory(FactoryAvro):
    def __init__(self, *args, **kwargs):
        super(CancerReportedVariantsFactory, self).__init__(*args, **kwargs)

    class Meta:
        model = ReportedVariantCancer

    _version = VERSION_300

    chromosome = factory.fuzzy.FuzzyChoice(list(map(str, range(1, 23))) + ['X', 'Y', 'MT'])
    position = factory.fuzzy.FuzzyInteger(1, 10000000)
    depthReference = factory.fuzzy.FuzzyInteger(1, 20)
    depthAlternate = factory.fuzzy.FuzzyInteger(1, 20)
    VAF = factory.fuzzy.FuzzyFloat(0, 1)
    commonAF = 0
    IHP = 0
    reference = factory.fuzzy.FuzzyChoice(['A', 'T', 'C', 'G'])
    alternate = factory.fuzzy.FuzzyChoice(['A', 'T', 'C', 'G'])



    @factory.post_generation
    def reportEvents(self, create, extacted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if not extacted:
            extacted = [
                ReportEventCancerFactory.create(),
                ]
        self.reportEvents = []
        for f in extacted:
            if f:
                self.reportEvents.append(f)



class ReportedSomaticVariantsFactory(FactoryAvro):
    def __init__(self, *args, **kwargs):
        super(ReportedSomaticVariantsFactory, self).__init__(*args, **kwargs)

    class Meta:
        model = ReportedSomaticVariants

    _version = VERSION_300

    reportedVariantCancer = factory.SubFactory(CancerReportedVariantsFactory)
    somaticOrGermline = 'somatic'


class CancerInterpretationRequestFactory(FactoryAvro):
    def __init__(self, *args, **kwargs):
        super(CancerInterpretationRequestFactory, self).__init__(*args, **kwargs)

    class Meta:
        model = CancerInterpretationRequest

    _version = VERSION_300

    reportVersion = 1
    reportRequestId = factory.Sequence(lambda n: 'CIPID-{}-1'.format(n))
    analysisUri = '/path/to/analisys/{}'.format(reportRequestId)
    BAMs = []
    bigWigs = []
    cancerParticipant = factory.SubFactory(CancerParticipantFactory)
    # internalStudyId = factory.fuzzy.FuzzyInteger(0, 10)
    structuralTieredVariants = []
    versionControl = VersionControl()
    workspace = factory.LazyAttribute(lambda gl: [factory.fuzzy.FuzzyText(length=4).fuzz()])
    interpretGenome = True
    analysisVersion = '1'
    additionalInfo = None
    annotationFile = None


    @factory.post_generation
    def VCFs(self, create, extacted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if not extacted:
            extacted = [
                FileFactory.create(fileType='VCF_somatic_SV'),
                FileFactory.create(fileType='VCF_somatic_small'),
                ]

        # A list of groups were passed in, use them
        self.VCFs = []
        for f in extacted:
            if f:
                self.VCFs.append(f)

    @factory.post_generation
    def TieredVariants(self, create, extacted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if not extacted:
            extacted = ReportedSomaticVariantsFactory.create_batch(10)

        # A list of groups were passed in, use them
        self.TieredVariants = []
        for f in extacted:
            if f:
                self.TieredVariants.append(f)



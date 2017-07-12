import factory.fuzzy
from protocols.util.dependency_manager import VERSION_400
from protocols.participant_1_0_0 import (
    CancerParticipant,
    TumourSample,
    VersionControl,
    MatchedSamples,
)
from protocols.util.factories.avro_factory import FactoryAvro


class CancerParticipantFactory(FactoryAvro):
    def __init__(self, *args, **kwargs):
        super(CancerParticipantFactory, self).__init__(*args, **kwargs)

    class Meta:
        model = CancerParticipant

    _version = VERSION_400

    versionControl = VersionControl()

    @factory.post_generation
    def cancerSamples(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if not extracted:
            extracted = [
                CancerSampleFactory.create(sampleType='germline'),
                CancerSampleFactory.create(sampleType='tumor'),
            ]

        # A list of groups were passed in, use them
        for f in extracted:
            self.cancerSamples = []
            if f:
                self.cancerSamples.append(f)
        self.matchedSamples = [
            MatchedSamples(
                germlineSampleId=extracted[0].sampleId,
                tumorSampleId=extracted[1].sampleId
            )
        ]


class CancerSampleFactory(FactoryAvro):
    def __init__(self, *args, **kwargs):
        super(CancerSampleFactory, self).__init__(*args, **kwargs)

    class Meta:
        model = TumourSample

    _version = VERSION_400

    labId = '1'
    preservationMethod = factory.fuzzy.FuzzyChoice(["FF", "FFPE"])
    phase = factory.fuzzy.FuzzyChoice(["PRIMARY"])

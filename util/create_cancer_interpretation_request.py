from protocols.reports_4_0_0 import CancerInterpretationRequest


def create_cancer_interpretation_request(
        analysisUri,
        annotationFile,
        bams,
        bigWigs,
        cancerParticipant,
        internalStudyId,
        reportRequestId,
        reportVersion,
        structuralTieredVariants,
        tieredVariants,
        tieringVersion,
        vcfs,
        versionControl,
        workspace,
        interpretGenome=True,
        analysisVersion='1',
        additionalInfo=None,
):
    # TODO(Greg): Add in migration if version is incorrect
    additionalInfo = {} if additionalInfo is None else additionalInfo
    return CancerInterpretationRequest(
        additionalInfo=additionalInfo,
        analysisUri=analysisUri,
        analysisVersion=analysisVersion,
        annotationFile=annotationFile,
        bams=bams,
        bigWigs=bigWigs,
        cancerParticipant=cancerParticipant,
        internalStudyId=internalStudyId,
        interpretGenome=interpretGenome,
        reportRequestId=reportRequestId,
        reportVersion=reportVersion,
        structuralTieredVariants=structuralTieredVariants,
        tieredVariants=tieredVariants,
        tieringVersion=tieringVersion,
        vcfs=vcfs,
        versionControl=versionControl,
        workspace=workspace,
    )

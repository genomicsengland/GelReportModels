version 2.3.0 (unreleased)
--------------------------
**RDParticipant.avdl**

* Minor Changes:
    - Added `yearOfBirth` to RDParticipant (optional field)

version 2.2.1 (26 May, 2016)
----------------------------
**CancerParticipant.avdl**

* Major Changes:
    - `Phase` and `Method` enumeration to upper case
    - Added `labkeyParticipantId` to `CancerDemographics`


version 2.2.0 (24 May, 2016)
----------------------------
**CancerParticipant.avdl**

* Major Changes:
    - `PreservationMethod`, `GelPhase` terms to upper case
    - `Sex` in `CancerParticipant` is defined now as `{M,F}`
    - Added `VersionControl` to `CancerSample` and `CancerDemographics`
    - Added `center` and `centerPatientId` to `CancerDemographics`, both are required

* Minor Changes:
    - `labId` and `sampleDiagnosis` in `CancerSample` can be null
    - `germlineSampleId` and `tumorSampleId` in `MatchedSamples` can be null
    - `primaryDiagnosis`, `sampleId` and `sex` can be null in `CancerDemographics`
    - Added `assignedICD10` to `CancerDemographics`


**GelBamMetrics.avdl**

* Major changes:
    - `PURITY_TUMOR_PLOIDY` and `PURITY_TUMOR_PURITY` are now double and, they can be null
    - Added `InsertSizeGel` (new record)

version 5.0.0 (13th November 2017)
--------------------------
* org.gel.models.cva.avro 0.4.0
    * First released version of CVA models
* org.gel.models.report.avro 4.2.0
    * ClinicalReportCancer refactored
    * ReportedVariantCancer refactored
    * CancerExitQuestionnaire
    * InterpretationRequestCancer refactored
    * InterpretedGenomeCancer refactored
* org.gel.models.system.avro 0.1.0
    * First version of the model to hold results from health checks

version 4.3.5 (2nd November 2017)
--------------------------
* reports 4.0.0
    - MD5 sum changed to a string
    - Other files added to the cancer interpretation request
    - New file types PARTITION, VARIANT_FREQUENCIES and COVERAGE
* Build system and package versioning refactored
* Python mock data factories

version 4.3.4 (20 Oct 2017)
-------------

* Minor changes:
    - Fixed erroneous import to participants_1_0_0 from participants migration

version 4.3.3 (18 Oct 2017)
-------------

* Minor changes:
    - Fixed erroneous import to participants_1_0_3_SNAPSHOT from participants migration

[...]

version 3.0.0 (unreleased)
--------------------------
**RDParticipant.avdl**

* Minor Changes:
    - Added `yearOfBirth` to `RDParticipant` (optional field)
    - Added `evidenceIds` to `ReportedVariant` and `ReportedStructuralVariant` (optional field)
    - Added new file types
    - Added md5Sum to `file` Record
    - Script to migrate models to new version has been added

* Major Changes:
    - More than one version is supported, currently 2.1.0 and 3.0.0
    - Added `ClinicalReportRD` a new model to communicate the clinical reports
    - Added `AuditLog` a new model to communicate Changes in the cases
    - Removed `VirtualPanel` model
    - `genotype` is now an enumeration
    - `ModeOfInheritance` removed from InterpretationRequest
    - `virtualPanel` removed from InterpretationRequest (this information is already at the family level)
    - `analysisVersion` is not mandatory anymore, please look at the documentation for this field

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

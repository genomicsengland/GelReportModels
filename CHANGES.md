Version 7.1.6 (24th August 2018)
--------------------------------

#### Minor changes

* Cancer participant snomed and ICD terms are not lists anymore
* `AlgorithmName` set to proper camel case
* Added `TIERA` and `TIERB`


Version 7.0.4 (2nd July 2018)
--------------------------------

#### Major changes

* CVA data intake models for pedigrees and cancer participant

Version 7.0.3
--------------------------------

#### Major changes

* Reported versus genetic models release

Version 7.0.2 (11th June 2018)
--------------------------------

#### Minor changes

* Putting back in `RareDiseaseInterpretationPipeline.avdl`

Version 7.0.1 (7th June 2018)
--------------------------------

#### Minor changes

* Putting back in backawards migration from participants 1.0.3 to 1.0.0

Version 7.0.1 (7th June 2018)
--------------------------------

#### Major changes

* New version for reports 6.0.0 supporting:
    - Structural variants in new format
    - Required for STRs support
    - Standardised phenotypes


Version 6.1.4 (1st June 2018)
--------------------------------

#### Major changes

* Models for reported versus genetic checks

Version 6.1.3 (1st June 2018)
--------------------------------

#### Major changes

* Backwards migrations from reports 5 to reports 3

Version 6.1.2 (18th May 2018)
--------------------------------

#### Minor changes

* Fix error in validation when the input entity is not a dict always returned True
* Added a method `equals()` to all objects to check equality

Version 6.1.1 (10th May 2018)
--------------------------------

#### Minor changes

* Migrations helpers for cancer entities
* Migration helper for RD exit questionnaire
* Migration testing strategy improved for migration helpers
* Several bugfixes in cancer migrations

Version 6.1.0 (3rd May 2018)
--------------------------------

#### Major Changes

* ReportEvent in cva package renamed to ReportEventRecord

#### Minor changes

* Migrations from participants 1.0.3 to 1.1.0
* Removed participants backwards migrations

Version 6.0.9 (1st May 2018)
--------------------------------

#### Minor Changes

* Migration helpers
* Fix bug migration called genotypes for structural variants
* Implement migration of disorders and HPO terms

Version 6.0.8 (27th April 2018)
--------------------------------

#### Minor Changes

* Bugfix IP-1169 tiering version lost in translation

Version 6.0.7 (27th April 2018)
--------------------------------

#### Minor Changes

* Bugfix IP-735 deserializing maps from JSON
* Bugfix IP-1094 fix lost HGNC
* Improved documentation
* Added `conversion_tools.py` as a script to python package

Version 6.0.6 (29th March 2018)
--------------------------------

#### Minor Changes

* Add backwards compatibility to mock data with the hotfix version
* Transaction.avdl including a field to keep track of cva version
* Package participants 1.0.1 is back into the build as it is used by `pythoncommonlibs`

Version 6.0.5 (28th March 2018)
--------------------------------

#### Minor Changes

* Transaction.avdl `TransactionStatus` having a new state `DELETED`
* Transaction.avdl having a record of transaction status changes in `TransactionStatusChange`

Version 6.0.4 (23rd March 2018)
--------------------------------

#### Minor Changes

* Transaction.avdl `TransactionStatus` having two new states `PROCESSING` and `PERSISTING`
* Transaction.avdl `TransactionStatus` has one less state `APPLIED`

Version 6.0.3 (22nd March 2018)
--------------------------------

### Major changes

* Remove hotfix version numbering from build version from 6.0 onwards. To generate any mock data from build 6.0 onwards, the string `6.0` is expected instead of `6.0.0`


#### Minor Changes

* Fixed `MigrateReports400To500().migrate_cancer_interpretation_request` and `MigrateReports400To500().migrate_interpretation_request_rd` that were failing when tested with nullable fields being null. Tests are improved
* Refactored migration tests to use `_validate`

Version 6.0.2 (21st March 2018)
--------------------------------

#### Minor Changes

* Migration of participants fixed for field `ageOfOnset` 


Version 6.0.1 (16th March 2018)
--------------------------------

#### Major Changes

* Exit questionnaire models have been updated with some changes that were lost back in the day merging `develop` and `master` branches. 


Version 6.0.0 (5th January 2018)
--------------------------------

#### Major Changes

##### org.gel.models.report.avro 5.0.0

###### Clinical Report Cancer

* `candidateVariants` renamed to `variants`

###### Clinical Report Rare Disease

* `candidateVariants` renamed to `variants`
* `supportingEvidences` renamed to `references`

###### ReportedVariant Rare Disease

* Renamed `calledGenotypes` to `variantCalls`
* `cosmicIds`, `clinVarIds`, `genomicChange`, `cdnaChanges` ,
`alleleFrequencies`, `alleleOrigins`, `flags` and `proteinChanges`
* `evidenceIds` renamed to `references`
* Variant coordinates `chromosome`, `position`, `reference` and
`alternate` has been refactored and move into  a new record
`VariantCoordinates`
* New record called `AlleleFrequencies`
* Renamed `gelId` to `participantId` in `VariantCall`
* Renamed `genotype` to `zygosity` in `VariantCall`
* Added `vaf` to `VariantCall` (nullable)
* Added `na` to `Zygosity` enum

###### Report Event (RD)

* `phenotype` is now an array of string and it is called `phenotypes`
* Added `consequenceTypes`
* Removed `panelName` and `panelVersion`, replaced by `genePanel`
* `VariantClassification` is now a complex object (defined in biodata)
* `penetrance` in `ReportEvent` is now nullable
* `score` in `ReportEvent` is now nullable
* `genomicFeature` in `ReportEvent` is now an array
* `hgnc` in `GenomicFeature` has been renamed to `geneSymbol`
* Added `intergenic` as a new Feature Type

###### Interpretation Request (RD and Cancer)
* Added `interpretationFlags` (nullable)

##### org.gel.models.participant.avro 1.1.0

###### Common participant

* `Sex` has now only one definition
* `SampleSource` has now only one definition

##### org.gel.models.cva.avro 1.0.0

* `SupportedAssembly` has been replaced by `org.gel.models.report.avro.Assembly`
* `Program` has been replaced by `org.gel.models.report.avro.Program`
* `VariantCoordinates` has been replaced by `org.gel.models.report.avro.VariantCoordinates`
* `CalledGenotype` has been replaced by `VariantCall`


version 5.0.0 (14th November 2017)
--------------------------

Minor changes
* `build.py` takes care of updating documentation indexes with option `--update-docs-index`
* Documentation updated

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

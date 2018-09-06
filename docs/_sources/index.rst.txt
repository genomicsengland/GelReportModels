.. g documentation master file, created by
   sphinx-quickstart on Thu Sep 22 17:00:21 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GEL models documentation
=============================

.. toctree::
    :maxdepth: 4

    index

Introduction
------------

GEL models project contains the data models that aim at standardizing data exchanges with Genomics England systems either internally or externally. This enables our data exchanges to be programming language and technology-agnostic.

Two illustrative examples:

* The CIPAPI exchanges data with the CIPs based on these models. This allows the CIPAPI to be completely independent of the specific implementations in the CIPs.
* The CIPAPI pushes data to CVA. While the CIPAPI is implemented as a Django application in Python, CVA is a Java application deployed in Tomcat.

The above exchanges are based on a REST interface, but any other technology could be used.

We use Avro to describe our models.

Packages
^^^^^^^^

The models are organised in packages:

* Participants: Demographic and Clinical Information
* Reports: Interpretation Request, Interpreted Genome, Clinical Reports
* Metrics: errr…. Metrics, yes
* Cva: Reported Variants and its Evidences
* Ga4gh: External. Variants and Alignments
* OpenCB: External(ish). Variants and Variant Annotation (and recently also evidences)

Main functionalities
^^^^^^^^^^^^^^^^^^^^

* Automatic code generation to hold the data (Python and Java supported out-of-the-box; others as C, C++ and C# are supported by ad hoc avro libraries).
* Enable data validation against a schema (see the validation service `https://github.com/genomicsengland/data-validation <https://github.com/genomicsengland/data-validation>` for additional validation business rules)
* Data serialisation/deserialisation to/from JSON
* Generation of mocked data
* Documentation automatically generated from the models

Resources
^^^^^^^^^

* Github repository: `https://github.com/genomicsengland/GelReportModels <https://github.com/genomicsengland/GelReportModels>`
* Models documentation: `https://genomicsengland.github.io/GelReportModels <https://genomicsengland.github.io/GelReportModels>`


Models Documentation
--------------------
.. toctree::
    :maxdepth: 4

    models

Installation
------------

Install built version from PyPIP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install from pip:
::

    pip install -i $PIP_SERVER GelReportModels


Or build locally
^^^^^^^^^^^^^^^^

Install ``sphynx``:
::

    sudo apt-get install python-sphinx


Install ``avrodoc``:
::

    sudo apt-get install nodejs nodejs-legacy
    sudo apt-get install npm
    sudo npm install avrodoc -g

Install python dependencies:
::

    pip install -r requirements.txt

Build the models
^^^^^^^^^^^^^^^^

To build all builds described in ``builds.json`` run:
::

    python build.py

This will create the following:
* Python source code representing the Avro records in the folder ``./protocols/models``
* Java source code representing the Avro records in the folder ``./target/generated-sources/avro``
* The models HTML documentation under ``./docs/html_schemas``

It may be handy to skip the documentation generation by using the flag ``--skip-docs``.

NOTE: Java source code is only generated for the last build version, while Python source code is generated for all versions

Building legacy versions of the models
""""""""""""""""""""""""""""""""""""""

See ``builds.json`` for the information on all legacy versions and the specific package versions and dependencies in each of those.

To build a specific version run:
::

    python build.py --version 3.0.0

Using custom tools to build the models
""""""""""""""""""""""""""""""""""""""

To facilitate using custom tools to build the models you can prepare the sandbox for a specific version running:
::

    python build.py --version 4.0.0 --only-prepare-sandbox

This will copy all required schemas for that build under the folder ``schemas/IDLs/build``.

Other build options
"""""""""""""""""""

Use ``--skip-docs`` to avoid generating documentation which affects build time greatly.

Use ``--skip-java`` to avoid generating Java source code.

Use ``--update-docs-index`` to update the documentation landing page with the latest documentation generated.

Java Packaging
^^^^^^^^^^^^^^

To pack the Java source code representing these models in a jar file use:
::

    % mvn package

To install it in your system so it is accessible as a maven dependency to other Java applications run:
::

    % mvn install

Unit tests
^^^^^^^^^^

To run some unit tests implemented in Python run:
::

    % ./run_tests.sh



Getting started
---------------

Serialisation to/from JSON
^^^^^^^^^^^^^^^^^^^^^^^^^^

Given that you hold your data in JSON format in a string in memory deserialise as follows:

::

    from protocols.reports_4_0_0 import CancerInterpretationRequest as CancerInterpretationRequest_4_0_0
    instance = CancerInterpretationRequest_4_0_0.fromJsonString(json_string)
    # now you can access the data in the instance
    print("This interpretation request has {} variants".format(instance.tieredVariants))

If your data is hold in a Python dictionary in memory deserialise as follows:

::

    instance = CancerInterpretationRequest_4_0_0.fromJsonDict(json_dict)

The object can be serialised into JSON as follows:

::

    instance.toJsonDict()
    instance.toJsonString()


Serialisation to/from AVRO
^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO

Schema validation
^^^^^^^^^^^^^^^^^

Validate any instance against the corresponding schema. This validation will ensure that all non-nullable fields are actually filled.
::

    # just Avro native validation
    is_valid = instance.validate(instance.toJsonDict())

    # verbose validation
    validation_object = instance.validate(instance.toJsonDict(), verbose=True)
    is_valid = validation_object.result
    if not is_valid
        print validation_object.messages


Mock data
^^^^^^^^^

Generate a mocked object or a batch of objects with custom fields as follows:
::

    from protocols.util.factories.avro_factory import GenericFactoryAvro

    # gets a default factory of InterpretationRequestRD for reports package 5.0.0 included in build 6.0.0
    factory = GenericFactoryAvro.get_factory_avro(
        protocols.reports_5_0_0.InterpretationRequestRD,
        version = '6.0.0'
    )
    # creates one mocked instance
    instance = factory.create()
    # creates a batch of mocked instances
    instances = factory.create_batch(5)
    # creates an instance with one custom value
    instance_with_uri = factory.create(analysisReturnUri = "myURI")

Get a factory that fills all nullable fields (nullable fields are not filled by default)
::

    # get an interpretation request RD for reports 4.2.0
    factory = GenericFactoryAvro.get_factory_avro(
        protocols.reports_5_0_0.CancerInterpretedGenome,
        version = '6.0.0',
        fill_nullables=True
    )

Generate custom factories as follows
::

    from protocols.ga4gh_3_0_0 import Variant
    from protocols.util.factories.avro_factory import FactoryAvro


    class GA4GHVariantFactory(FactoryAvro):
        def __init__(self, *args, **kwargs):
            super(GA4GHVariantFactory, self).__init__(*args, **kwargs)

        class Meta:
            model = Variant

        _version = '6.0.0'

        start = factory.fuzzy.FuzzyInteger(1, 10000000)
        referenceBases = factory.fuzzy.FuzzyChoice(['A', 'T', 'C', 'G'])
        alternateBases = factory.LazyAttribute(lambda x: [factory.fuzzy.FuzzyChoice(['A', 'T', 'C', 'G']).fuzz()])
        qual = factory.fuzzy.FuzzyInteger(1, 600)
        referenceName = factory.fuzzy.FuzzyChoice(list(map(str, range(1, 23)) + ['X', 'Y', 'MT']))

    factory = GA4GHVariantFactory
    variant = factory()
    variants = factory.create_batch(3)


Migrations
^^^^^^^^^^

There a number of migration scripts in the package `protocols.migration`. They can be used as follows:

::

    from protocols.reports_4_0_0 import CancerInterpretationRequest as CancerInterpretationRequest_4_0_0
    from protocols.reports_5_0_0 import CancerInterpretationRequest as CancerInterpretationRequest_5_0_0
    from protocols.util.dependency_manager import VERSION_400
    from protocols.migration.migration_reports_4_0_0_to_reports_5_0_0 import MigrateReports400To500

    old_instance = GenericFactoryAvro.get_factory_avro(CancerInterpretationRequest_4_0_0, VERSION_400).create()
    old_instance.validate(old_instance.toJsonDict())

    migrated_instance = MigrateReports400To500().migrate_cancer_interpretation_request(
        old_instance=old_instance, assembly='GRCh38'
    )
    migrated_instance.validate(migrated_instance.toJsonDict())

Building Resources From a Container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From your starting directory, eg. ~/src/:

Clone this repo
::

    git@github.com:genomicsengland/GelReportModels.git

Then run the following (you may need `sudo` depending on your system configuration):

::

    ./build_models

Once the build is successful, check the resources are there:
::

    root@e444d27c16b9:/gel# ls GelReportModels/protocols/
    GelProtocols.pyc      cva_0_3_0.py      migration                 protocol.py
    __init__.py           ga4gh.py          opencb.py                 protocol.pyc
    __init__.pyc          ga4gh_3_0_0.py    opencb_1_2_0-SNAPSHOT.py  reports.py
    catalog_variable_set  metrics.py        participant.py            reports_2_1_0.py
    cva.py                metrics_1_0_0.py  participant_1_0_0.py      reports_3_0_0.py
    root@e444d27c16b9:/gel#

Also check that Java resources are there:
::

    root@4dabae77118d:/gel# ls -l GelReportModels/target/
    total 53620
    drwxr-xr-x  2 root root     4096 Aug 18 08:35 antrun
    drwxr-xr-x  3 root root     4096 Aug 18 08:45 classes
    drwxr-xr-x  2 root root     4096 Aug 18 08:35 dependency-maven-plugin-markers
    drwxr-xr-x 17 root root     4096 Aug 18 08:55 gel-models-4.3.0-SNAPSHOT
    -rw-r--r--  1 root root  1819234 Aug 18 08:45 gel-models-4.3.0-SNAPSHOT.jar
    -rw-r--r--  1 root root 53054906 Aug 18 08:55 gel-models-docs-4.3.0-SNAPSHOT.war
    drwxr-xr-x  4 root root     4096 Aug 18 08:45 generated-sources
    drwxr-xr-x  2 root root     4096 Aug 18 08:45 maven-archiver
    drwxr-xr-x  3 root root     4096 Aug 18 08:45 maven-status

then in a separate tab/window, from the GelReportModels directory:
::

    sudo docker ps -alq containerID

and use this container ID to copy the python files from GelReportModels/protocols:
::

    sudo docker cp containerID:/GelReportModels/protocols .

then check you have them present:
::

    $ ls ./protocols/
    catalog_variable_set  GelProtocols.pyc  migration                 protocol.py
    cva_0_3_0.py          __init__.py       opencb_1_2_0-SNAPSHOT.py  protocol.pyc
    cva.py                __init__.pyc      opencb.py                 reports_2_1_0.py
    ga4gh_3_0_0.py        metrics_1_0_0.py  participant_1_0_0.py      reports_3_0_0.py
    ga4gh.py              metrics.py        participant.py            reports.py

Additional tools
^^^^^^^^^^^^^^^^

The conversion between the different Avro schema formats, source code and documentation are available through the following script:
::

    $ conversion_tools.py --help
    usage: conversion_tools.py <command> [<args>]

    GEL models toolbox

    positional arguments:
      command     Subcommand to run
                  (idl2json|idl2avpr|json2java|idl2python|json2python|avpr2html|update_docs_index)

    optional arguments:
      -h, --help  show this help message and exit
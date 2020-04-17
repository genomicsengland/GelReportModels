
# GelReportModels

This project contains several models used by Genomics England systems. This is a development guide, the models documentation can be found at [https://gelreportmodels.genomicsengland.co.uk](https://gelreportmodels.genomicsengland.co.uk). 


These models are defined using Avro Interface Design Language (IDL) which is agnostic of any implementation language. The models are then used to generate source code employed to store the information. The source code is either Python or Java so far, but this can be easily extended.

From the Avro models you can generate:
* Java source code
* Python source code
* JSON schemas
* AVPR schemas
* HTML documentation

Maven is employed for Java dependency management. Particularly, OpenCB [https://github.com/opencb/biodata](https://github.com/opencb/biodata) models are imported through a maven dependency and then extracted into the local folder for schemas.
This is not required unless you upgrade OpenCB models version, as the OpenCB models are commited in the repository under `schemas/IDLs/org.opencb.biodata.models`.

To import the OpenCB dependency and extract the models in your local environment run:
```
% mvn clean initialize
```

## Versioning

Models are organised in **packages**:
* Internal
    - org.gel.models.report.avro
    - org.gel.models.participant.avro
    - org.gel.models.metrics.avro
    - org.gel.models.cva.avro
    - org.gel.models.system.avro
* External
    - org.ga4gh.models
    - org.opencb.biodata.models
    
A package is formed by a set of **schema files** having `.avdl` extension.

There are dependencies between packages that require that we **build** packages together.
    
Each of those packages support independent versioning. Also there are build versions that determine a set of specific packages that are built together. These information is contained within `builds.json` in an array of build descriptions.

The following represents the build version `4.3.0-SNAPSHOT` having package org.ga4gh.models version 3.0.0, package org.gel.models.cva.avro version 0.4.0-SNAPSHOT and so on.
```
{
  "version": "4.3.0-SNAPSHOT",
  "packages": [
    {
      "package": "org.ga4gh.models",
      "python_package": "ga4gh",
      "version": "3.0.0",
      "dependencies": []
    },
    {
      "package": "org.gel.models.cva.avro",
      "python_package": "cva",
      "version": "0.4.0-SNAPSHOT",
      "dependencies": [
        "org.gel.models.report.avro",
        "org.gel.models.participant.avro",
        "org.gel.models.system.avro",
        "org.opencb.biodata.models"
      ]
    },
    {
      "package": "org.gel.models.metrics.avro",
      "python_package": "metrics",
      "version": "1.1.0-SNAPSHOT",
      "dependencies": []
    },
    {
      "package": "org.gel.models.participant.avro",
      "python_package": "participant",
      "version": "1.0.4-SNAPSHOT",
      "dependencies": []
    },
    {
      "package": "org.gel.models.report.avro",
      "python_package": "reports",
      "version": "4.2.0-SNAPSHOT",
      "dependencies": [
        "org.gel.models.participant.avro"
      ]
    },
    {
      "package": "org.gel.models.system.avro",
      "python_package": "system",
      "version": "0.1.0-SNAPSHOT",
      "dependencies": []
    },
    {
      "package": "org.opencb.biodata.models",
      "python_package": "opencb",
      "version": "1.3.0-SNAPSHOT",
      "dependencies": []
    }
  ]
}
```

Every package in a build is built in a sandbox folder under `schemas/IDLs/build` together with those packages in the list of dependencies for each package. This introduces two strong constraints in the models:
* The same package cannot contain two records named equally in different schema files
* Schema files in different packages cannot be named equally
 
The build sandbox is deleted after every build.


## Getting started

### Install requirements

Install `sphynx`:
```
sudo apt-get install python-sphinx
```

Install `avrodoc`:
```
sudo apt-get install nodejs nodejs-legacy
sudo apt-get install npm
sudo npm install avrodoc -g
```

Install python dependencies:
```
pip install -r requirements.txt
```

### Build the models

To build all builds described in `builds.json` run:
```
% python build.py
```

This will create the following:
* Python source code representing the Avro records in the folder `./protocols/models`
* Java source code representing the Avro records in the folder `./target/generated-sources/avro`
* The models HTML documentation under `./docs/html_schemas`

It may be handy to skip the documentation generation by using the flag `--skip-docs`.

#### Building legacy versions of the models

See `builds.json` for the information on all legacy versions and the specific package versions and dependencies in each of those.

To build a specific version run:
```
% python build.py --version 3.0.0
```

#### Using custom tools to build the models

To facilitate using custom tools to build the models you can prepare the sandbox for a specific version running:
```
% python build.py --version 4.0.0 --only-prepare-sandbox
```

This will copy all required schemas for that build under the folder `schemas/IDLs/build`.

#### Other build options

Use `--skip-docs` to avoid generating documentation which affects build time greatly.

Use `--skip-java` to avoid generating Java source code.

Use `--update-docs-index` to update the documentation landing page with the latest documentation generated.

### Java Packaging

To pack the Java source code representing these models in a jar file use:
```
% mvn package
```

To install it in your system so it is accessible as a maven dependency to other Java applications run:
```
% mvn install
```

## Unit tests

To run some unit tests implemented in Python run:
```
% ./run_tests.sh
```

## Mock data

Generate a mocked object with custom fields as follows:
```
from protocols.util.dependency_manager import VERSION_500
from protocols.util.factories.avro_factory import GenericFactoryAvro

interpretation_request_factory = GenericFactoryAvro.get_factory_avro(
    protocols.reports_4_2_0.InterpretationRequestRD,
    version = VERSION_500
)
instance = interpretation_request_factory(analysisReturnUri = "myURI")
self.assertTrue(instance.validate(instance.toJsonDict()))
self.assertTrue(instance.analysisReturnUri == "myURI")
```

## Migrations
TODO

## Building Resources From a Container
From your starting directory, eg. ~/gel/:

Clone this repo
```
git@github.com:genomicsengland/GelReportModels.git
```

Then run the following (you may need `sudo` depending on your system configuration):

```
./build_models
```
Once the build is successful, check the resources are there:
```
root@e444d27c16b9:/gel# ls GelReportModels/protocols/
GelProtocols.pyc      cva_0_3_0.py      migration                 protocol.py
__init__.py           ga4gh.py          opencb.py                 protocol.pyc
__init__.pyc          ga4gh_3_0_0.py    opencb_1_2_0-SNAPSHOT.py  reports.py
catalog_variable_set  metrics.py        participant.py            reports_2_1_0.py
cva.py                metrics_1_0_0.py  participant_1_0_0.py      reports_3_0_0.py
root@e444d27c16b9:/gel# 
```

Also check that Java resources are there:
```
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
```

then in a separate tab/window, from the GelReportModels directory:
```
$ sudo docker ps -alq
containerID
```
and use this container ID to copy the python files from GelReportModels/protocols:
```
$ sudo docker cp containerID:/GelReportModels/protocols .
```
then check you have them present:
```
$ ls ./protocols/
catalog_variable_set  GelProtocols.pyc  migration                 protocol.py
cva_0_3_0.py          __init__.py       opencb_1_2_0-SNAPSHOT.py  protocol.pyc
cva.py                __init__.pyc      opencb.py                 reports_2_1_0.py
ga4gh_3_0_0.py        metrics_1_0_0.py  participant_1_0_0.py      reports_3_0_0.py
ga4gh.py              metrics.py        participant.py            reports.py
```

## Additional tools

The conversion between the different Avro schema formats, source code and documentation are available through the following utility:
```
$ cd resources/GelModelsTools/
$ python gel_models_tools.py --help
usage: gel_models_tools.py <command> [<args>]

GEL models toolbox

positional arguments:
  command     Subcommand to run
              (idl2json|idl2avpr|json2java|idl2python|json2python|avpr2html)

optional arguments:
  -h, --help  show this help message and exit
```

## Deploying

To deploy to GELs internal pypi instance, run the `GEL-models/Deploy GelReportModels into Pypi` bio jenkins job and this will automate the deploy. 

To deploy to public PyPi you can use one of the Dockerfiles in this repo. Create an image and run it as follows:


    docker build -f Dockerfile-python3 .
    docker run -it <hashname> /bin/bash

Once inside the container you need to create a file called ~/.pypirc with contents as follows: 

```
[distutils]
index-servers =
    pypi

[pypi]
repository: https://upload.pypi.org/legacy/
username: <your username>
password: <your password>
```

Once you have this file, you can run the following commands:

```bash
python3 build.py --skip-java --skip-docs

pip3 install --upgrade twine wheel setuptools keyrings.alt
python3 setup.py sdist bdist_wheel

twine upload dist/GelReportModels-7.3.6.tar.gz
```
 
See https://packaging.python.org/tutorials/packaging-projects/



# GelReportModels

This project contains several models used by GEL. These models are defined using Avro Interface Design Language (IDL) which is agnostic of any implementation language. The models are then used to generate source code employed to store the information. The source code is either Python or Java so far, but this can be easily extended.

From the Avro models you can generate:
* Java source code
* Python source code
* JSON schemas
* AVPR schemas
* HTML documentation

Maven is employed to manage the source code generation and dependency management.
Nevertheless, to configure the development environment some of the OpenCB dependencies must compiled and installed locally.
* `biodata` contains the Avro models in OpenCB. Clone the appropriate branch and install it locally
```$shell
git clone git@github.com:opencb/biodata.git
git checkout feature-improveclinical
mvn clean install -DskipTests
```

To generate sources and documentation run:
```
% mvn clean generate-sources
```
This will create a set of Java classes representing the Avro records in the folder `./target/generated-sources/avro`. A set of Python classes under `./protocols/models`. The models documentation under `./docs/html_schemas`

To run against a legacy version of the models by overriding maven properties run:
```
% mvn clean generate-sources -Dreport.models.version=2.1.0
```

To pack the Java source code representing these models in a jar file use:
```
% mvn package
```

To install it in your system so it is accessible as a maven dependency to other applications run:
```
% mvn install
```

To create a war file containing the HTML documentation for the models and the models itself run:
```
% mvn package -Dp.type=war
```
This war can be deployed as a documentation service.


## OpenCB dependencies

The CVA model is extending the OpenCB variant model. In order to do so we need some Avro definitions from OpenCB biodata-models. Maven is extracting the required files from the biodata-models.jar file and use them to generate the required sources.
Current version relies on biodata [v1.2.0](https://github.com/opencb/biodata/tree/v1.2.0)

## Dependencies

* **npm**: to install run `apt-get install npm`
* **node**: to install run `apt-get install nodejs nodejs-legacy`
* **Avrodoc**: to install avrodoc run `npm install avrodoc -g`
* **pip**: to install pip run `apt-get install pip`
* Other python dependencies documented in `requirements.txt` should be installed automatically.

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

If the files you require are not present then you may need to build them with the following command:
```
% mvn clean generate-sources -D{package_name}={package_version}
```

where `<package_name>` can be one (or many, space separated) names from this (non-exhaustive) list:
```
org.gel.models.participant.avro
org.gel.models.metrics.avro 
org.ga4gh.models
org.gel.models.report.avro 
org.gel.models.report.avro
```

where the package names correspond with the schemas available in the [/schemas/IDLS](https://github.com/genomicsengland/GelReportModels/tree/develop/schemas/IDLs)  directory

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

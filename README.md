
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
This will create a set of Java classes representing the Avro records in the folder `./target/generated-sources/avro`. A set of Python classes under `./protocols/models`. The models documentation under `./docs/html_schemas/latest`

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

Clone the `java-commons-lib`
```
git clone git@github.com:opencb/java-common-libs.git
```

Clone the `biodata` `feature-improveclinical` branch
```
git clone -b feature-improveclinical git@github.com:opencb/biodata.git
```

Put this into a Dockerfile:
```
FROM ubuntu:16.04
RUN apt-get update && \
    apt-get install -y build-essential python openjdk-8-jdk maven \
    python-dev python-pip python-virtualenv postgresql \
    postgresql-contrib libpq-dev \
    libsasl2-dev libldap2-dev libssl-dev \
    npm nodejs nodejs-legacy && \
    npm install avrodoc -g
ENV PYTHONUNBUFFERED 1
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64
RUN mkdir /gel
RUN mkdir /gel/GelReportModels
RUN mkdir /gel/java-common-libs
RUN mkdir /gel/biodata
WORKDIR /gel
ADD GelReportModels /gel/GelReportModels/
ADD java-common-libs /gel/java-common-libs/
ADD biodata /gel/biodata/
RUN cd GelReportModels && \ 
    pip install --upgrade pip && \ 
    pip install -r requirements.txt && \
    cd ../java-common-libs && \
    mvn clean install -DskipTests && \
    cd ../biodata && \
    mvn clean install -DskipTests && \
    pip install --upgrade pysam && \
    mvn clean generate-sources && \
    cd ../GelReportModels && \
    mvn clean generate-sources
```

and run the following:

```
sudo docker build -t gel . && sudo docker run -it gel
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

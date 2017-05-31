
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
* **Other python dependencies** to be installed with pip
```
yaml
sphinx
sphinx_rtd_theme
ujson==1.33
avro==1.7.7
humanize==0.5.1
PyYAML==3.11
```

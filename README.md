
# GelReportModels

This project contains several models used by GEL. These models are defined using Avro Interface Design Language (IDL) which is agnostic of any implementation language. The models are then used to generate source code employed to store the information. The source code is either Python or Java so far, but this can be easily extended.

## Java source code

Maven is employed to manage the source code generation and dependency management.

To generate sources run: 
```
% mvn generate-sources
```
This will create a set of classes representing the Avro records in the folder `./target/generated-sources/avro`.


To pack the Java source code representing these models in a jar file use:
```
% mvn package
```

To install it in your system so it is accesible as a maven dependency to other applications run:
```
% mvn install
```

To create a war file containing the HTML documentation for the models and the models itself run:
```
% mvn package -Dp.type=war
```


### OpenCB dependencies

The CVA model is extending the OpenCB variant model. In order to do so we need some Avro definitions from OpenCB biodata-models. Maven is extracting the required files from the biodata-models.jar file and use them to generate the required sources.

## Model documentation

The model documentation is at `./src/main/html/model-documentation.html`. This documentation has been generated with `avrodoc` (https://github.com/ept/avrodoc). To regenerate it run:
```
# creates *.avsc files from *.avdl
% mvn generate-sources
# generates html from the schemas
% avrodoc target/generated-sources/avsc/* > ./src/main/html/model-documentation.html
```

**NOTE**: to install avrodoc run `npm install avrodoc -g`
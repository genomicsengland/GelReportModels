
# GelReportModels

This project contains several models used by GEL. These models are specified by using Avro Interface Design Language (IDL) which is agnostic of any language. The models are then used to generate source code employed to store the information. The source code is either Python or Java so far, but this can be easily extended.

## Java source code

Maven is employed to manage the source code generation and dependency management.

To generate sources run: 
```
mvn generate-sources
```
This will create a set of classes representing the Avro records in the folder `./target/generated-sources/avro`.


To pack the Java source code representing these models in a jar file use:
```
mvn package
```

### Data Transfer Objects

In order to add logic to the generated sources we create a set of wrapper classes that take care of containing the Avro object and assure that the information is valid. These are the classes that will be used by external applications.
These classes are under `./src/main/java`.

### OpenCB dependencies

The CVA model is extending the OpenCB variant model. In order to do so we need some *.avdl files from biodata-models. Maven is extracting the required files from the biodata-models.jar file and use them to generate the required sources.
Instalation
===========

This is a quick guide to build and install the GelModels, this is project has three well defined different parts:
Models definitions, python implementation and converters.

.. note::
    You can use the model definition as them self, if this is your case and you are not interested in use the clases from
    python it is not necesary follow this guide

Several consideration has to be taken in acount before to start the installation process: This packages provide a code generation
form AVRO schema, that means that the code of the python clases in this package were automatically generated, so if you have made
any change in the model you should build the classes again, otherwise wont be equivalent to your new version.

Build the python classes
------------------------

After any change in the .avdl files you should build the python classes, to do this you have to run the "build.py" to the root of the project::

    cd GelReportModels
    python build.py

This script is going to:

    1 Generate the .asvc files for the idl files (these files are necesaries to generate the code, so you could use it to generate java classes)
    2 Generate a file called GelProtocol.py to know more about the GelProtocol module please read this. This classes must
     not be modified in any case directly, but using the .avdl

.. note::
    Please note if you are not making modification in the idl files you can skip this step

Installation
------------

Once the classes are created if you want to have them in your system as python just type::

    sudo pip install . --update
if you are not use pip you can install the project with::

    sudo python setup.py install




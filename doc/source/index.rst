.. GelModels documentation master file, created by
   sphinx-quickstart on Thu Sep  3 09:13:15 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to GelModels's documentation!
=====================================

Previous consideration
----------------------

This is a project created to hold the data models using in the bioinformatics team in Genomics England, but on top of
that this model are a general representation of genetics data taken as pattern the model developed by GA4GH and extended
the functionality not only to genomic concepts as "variant" or "read" but also to general genetics data as pedigree, sample or
even interpreted genomes.

You are going to find in this project definition for data you need to start an genomic analysis for families and cancer samples,
the result of this genomic analysis. This was created from the vision of the Genomic England Project, but could be extensive
to any human genomic project of rare diseases and cancer.

Before to make any change in the project you have to understand that it is very sensitive, since it defines important
piece of information in the Genomics England project, however we are happy to consider all the suggestion to improve it.
You should read the guide for developer before to start consider make propose changes.

Ths project use AVRO schema to define the models, AVRO is a efficient way to serialize data, and can the schemas can be used
to define the code through code generators. There are two ways to define an AVRO model using an idl format (avdl) or
using a json format (avsc). They are interconvertibles???,  we choose the idl format to build our model since it is easily human readable.
And we also provide short-cuts to convert this idls in json files and in python classes, for this we use the general tools for avro
from Apache and the GA4GH implementation for python.

Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


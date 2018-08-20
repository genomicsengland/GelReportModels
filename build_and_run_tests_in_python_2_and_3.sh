#!/usr/bin/env bash
docker build -t gelreportmodels:python2 -f Dockerfile-python2 .
docker build -t gelreportmodels:python3 -f Dockerfile-python3 .

docker run -v ${PWD}:/code -w /code gelreportmodels:python3 python3 build.py --skip-docs --skip-java
docker run -v ${PWD}:/code -w /code gelreportmodels:python3 python3 -m unittest discover .
docker run -v ${PWD}:/code -w /code gelreportmodels:python2 python -m unittest discover .
#!/usr/bin/env bash
coverage run --source=protocols -m unittest discover -s protocols/ && coverage report --omit="*test*" --omit="*__init__*"

import json
from distutils.core import setup
import os
from pip.req import parse_requirements
import uuid

install_reqs = parse_requirements(os.path.join(os.path.dirname(__file__), "requirements.txt"), session=uuid.uuid1())
reqs = [str(ir.req) for ir in install_reqs if ir.req is not None]

BASE_DIR = os.path.dirname(__file__)
VERSION = json.load(open(os.path.join(BASE_DIR, "schemas", "JSONs", "VersionControl", "VersionControl.avsc")))["fields"][0]["default"]
setup(
    name='GelReportModels',
    version=VERSION,
    packages=['protocols'],
    url='',
    license='',
    author='Bioinformatics Team at Genomics England',
    author_email='antonio.rueda-martin@genomicsengland.co.uk',
    description='Bioinformatics team model definitions',
    install_requires=reqs,
)

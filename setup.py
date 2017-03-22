import json
from distutils.core import setup
reqs = [
    "sphinx_rtd_theme",
    "labkey",
    "ujson==1.33",
    "avro==1.7.7",
    "humanize==0.5.1",
    "PyYAML==3.11",
    "pysam"
]

# BASE_DIR = os.path.dirname(__file__)
# VERSION = json.load(open(os.path.join(BASE_DIR, "schemas", "JSONs", "VersionControl", "VersionControl.avsc")))["fields"][0]["default"]
VERSION = "3.0.8"
setup(
    name='GelReportModels',
    version=VERSION,
    packages=['protocols'],
    scripts=['scripts/ModelValidator'],
    url='',
    license='',
    author='Bioinformatics Team at Genomics England',
    author_email='antonio.rueda-martin@genomicsengland.co.uk',
    description='Bioinformatics team model definitions',
    install_requires=reqs,
)

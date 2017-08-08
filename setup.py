import os
from setuptools import find_packages, setup
# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


reqs = [
    "sphinx_rtd_theme",
    "labkey",
    "ujson==1.33",
    "avro==1.7.7",
    "humanize==0.5.1",
    "PyYAML==3.11",
    "pysam"
]

VERSION = "4.1.1"
setup(
    name='GelReportModels',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    scripts=['bin/ModelValidator'],
    url='',
    license='',
    author='Bioinformatics Team at Genomics England',
    author_email='antonio.rueda-martin@genomicsengland.co.uk',
    description='Bioinformatics team model definitions',
    install_requires=reqs
)

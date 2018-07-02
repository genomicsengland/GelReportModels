import os
from setuptools import find_packages, setup
# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


reqs = [
    "Sphinx==1.6.2",
    "sphinx_rtd_theme==0.2.4",
    "avro==1.7.7",
    "factory-boy==2.9.2",
    "humanize==0.5.1",
    "PyYAML==3.12",
    "ujson==1.35",
    "dictdiffer"
]

VERSION = "7.0.4"
setup(
    name='GelReportModels',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    scripts=['bin/ModelValidator', 'protocols_utils/utils/conversion_tools.py'],
    url='',
    license='',
    author='Bioinformatics Team at Genomics England',
    author_email='antonio.rueda-martin@genomicsengland.co.uk',
    description='Bioinformatics team model definitions',
    install_requires=reqs
)

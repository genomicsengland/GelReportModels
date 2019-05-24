import os
import sys
from setuptools import find_packages, setup
# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

reqs = [
    "Sphinx==1.6.2",
    "sphinx_rtd_theme==0.2.4",
    "factory-boy==2.9.2",
    "humanize==0.5.1",
    "pyyaml>=4.2b1",
    "ujson==1.35",
    "dictdiffer",
    "future==0.16.0"
]

enforced_version = os.environ.get("GEL_REPORT_MODELS_PYTHON_VERSION", None)
interpreter_version = str(sys.version_info[0])
target_version = enforced_version if enforced_version else interpreter_version
if target_version == '2':
    reqs += ["avro==1.7.7"]
elif target_version == '3':
    reqs += ["avro-python3==1.8.2"]
else:
    raise ValueError("Not supported python version {}".format(target_version))

VERSION = "7.2.9"
setup(
    name='GelReportModels',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    scripts=['bin/ModelValidator', 'protocols_utils/utils/conversion_tools.py',
             'protocols_utils/utils/migration_test_real_data_rd.py',
             'protocols_utils/utils/migration_test_real_data_cancer.py'],
    url='https://github.com/genomicsengland/GelReportModels',
    download_url="https://github.com/genomicsengland/GelReportModels/archive/v{}.tar.gz".format(VERSION),
    license='Apache',
    author='Bioinformatics Team at Genomics England',
    author_email='antonio.rueda-martin@genomicsengland.co.uk',
    description='Genomics England Bioinformatics team model definitions',
    install_requires=reqs
)

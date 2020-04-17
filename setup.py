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
    "dictdiffer",
    "future==0.16.0",
    "six"
]

enforced_version = os.environ.get("GEL_REPORT_MODELS_PYTHON_VERSION", None)
interpreter_version = str(sys.version_info[0])
target_version = enforced_version if enforced_version else interpreter_version
if target_version == '2':
    reqs += ["avro==1.7.7"]
    # FileNotFoundError is only available since Python 3.3
    FileNotFoundError = IOError
    from io import open
elif target_version == '3':
    reqs += ["avro-python3==1.8.2"]
else:
    raise ValueError("Not supported python version {}".format(target_version))

VERSION = "7.4.2"

# read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='GelReportModels',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    scripts=['bin/ModelValidator', 'protocols_utils/utils/conversion_tools.py',
             'protocols_utils/utils/migration_test_real_data_rd.py',
             'protocols_utils/utils/migration_test_real_data_cancer.py'],
    url='https://gelreportmodels.genomicsengland.co.uk',
    download_url="https://github.com/genomicsengland/GelReportModels/archive/v{}.tar.gz".format(VERSION),
    license='Apache',
    author='Bioinformatics Team at Genomics England',
    author_email='antonio.rueda-martin@genomicsengland.co.uk',
    description='Genomics England Bioinformatics team model definitions',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=reqs,
    classifiers=[
        'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ]
)

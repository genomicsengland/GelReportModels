from distutils.core import setup
import os
from pip.req import parse_requirements
import uuid

install_reqs = parse_requirements(os.path.join(os.path.dirname(__file__), "requirements.txt"), session=uuid.uuid1())
reqs = [str(ir.req) for ir in install_reqs if ir.req is not None]
setup(
    name='GelReportModels',
    version='1.1.4',
    packages=['protocols'],
    url='',
    license='',
    author='Bioinformatics Team at Genomics England',
    author_email='antonio.rueda-martin@genomicsengland.co.uk',
    description='Bioinformatics team model definitions',
    install_requires=reqs,
)

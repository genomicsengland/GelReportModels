from distutils.core import setup
from pip.req import parse_requirements
install_reqs = parse_requirements("requirements.txt")
reqs = [str(ir.req) for ir in install_reqs]
setup(
    name='GelReportModels',
    version='v1.1.1',
    packages=['protocols'],
    url='',
    license='',
    author='Bioinformatics Team at Genomics England',
    author_email='antonio.rueda-martin@genomicsengland.co.uk',
    description='Bioinformatics team model definitions',
    install_requires=reqs,
)

from distutils.core import setup
from smpteparsers import __version__

setup(
    name = 'smpteparsers',
    version = __version__,
    description = 'A set of python parsers for various SMPTE standards.',
    author = 'Arts Alliance Media',
    author_email = 'dev@artsalliancemedia.com',
    url = 'http://www.artsalliancemedia.com',
    packages = ('smpteparsers',),
    requires = ('beautifulsoup4==4.2.1', 'lxml==3.2.1', 'requests==1.2.3', 'jsonschema==2.3.0'),
    extras_require = {"docs": ("sphinx",)}
)

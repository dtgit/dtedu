"""Marshall - Configurable Marshallers for Archetypes

Marshall enables one to selectively choose which marshaller gets
enabled depending on various aspects of the incoming request.
"""

classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Web Environment
License :: OSI Approved :: GNU General Public License (GPL)
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Zope
Topic :: Internet :: WWW/HTTP
Topic :: Internet :: File Transfer Protocol (FTP)
"""

import os
import sys
from setuptools import setup, find_packages

# We're using the module docstring as the distutils descriptions.
doclines = __doc__.split("\n")
NAME = 'Marshall'
VERSION = open('version.txt').read().strip()

data = dict(
    name=NAME,
    version=VERSION,
    author="Sidnei da Silva",
    author_email="sidnei@enfoldsystems.com",
    keywords="web zope application server webdav ftp",
    url="http://www.enfoldsystems.com",
    download_url="http://enfoldsystems.com/Products/Open/Marshall-%s.tar.gz" % VERSION,
    license="Zope Public License",
    platforms=["any"],
    description=doclines[0],
    classifiers=filter(None, classifiers.split("\n")),
    long_description="\n".join(doclines[2:]),
    zip_safe=False)

packages = find_packages()
package_dir = {NAME: ''}
for package in packages:
    package_dir['%s.%s' % (NAME, package)] = os.sep.join(package.split('.'))

data['packages'] = package_dir.keys()
data['package_dir'] = package_dir

setup(**data)

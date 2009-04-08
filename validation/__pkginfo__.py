from Products import validation as PRODUCT

version=PRODUCT.__version__
modname=PRODUCT.__name__

# (major, minor, patchlevel, release info) where release info is:
# -99 for alpha, -49 for beta, -19 for rc and 0 for final
# increment the release info number by one e.g. -98 for alpha2

major, minor, bugfix =  version.split('.')[:3]
bugfix, release = bugfix.split('-')[:2]

relinfo=-99 #alpha
if 'beta' in release:
    relinfo=-49
if 'rc' in release:
    relinfo=-19
if 'final' in release:
    relinfo=0

numversion = (int(major), int(minor), int(bugfix), relinfo)

license = 'BSD (ish)'
copyright = '''Benjamin Saller (c) 2003'''

author = "Archetypes developement team"
author_email = "archetypes-devel@lists.sourceforge.net"

short_desc = "Some generic validators originaly defined for Archetypes"
long_desc = short_desc

web = "http://plone.org/products/archetypes"
ftp = ""
mailing_list = "archetypes-devel@lists.sourceforge.net"

debian_maintainer = "Sylvain Thenault"
debian_maintainer_email = "sylvain.thenault@logilab.fr"
debian_handler = "python-library"

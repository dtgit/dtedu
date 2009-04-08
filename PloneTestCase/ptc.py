#
# PloneTestCase API
#

# $Id: ptc.py 54876 2007-12-04 16:02:36Z shh42 $

from Testing.ZopeTestCase import hasProduct
from Testing.ZopeTestCase import installProduct

try:
    from Testing.ZopeTestCase import hasPackage
    from Testing.ZopeTestCase import installPackage
except ImportError:
    pass

from Testing.ZopeTestCase import Sandboxed
from Testing.ZopeTestCase import Functional

from Products.PloneTestCase import utils
from Products.PloneTestCase.utils import *

from Products.PloneTestCase import setup
from Products.PloneTestCase.setup import PLONE21
from Products.PloneTestCase.setup import PLONE25
from Products.PloneTestCase.setup import PLONE30
from Products.PloneTestCase.setup import PLONE31
from Products.PloneTestCase.setup import PLONE40
from Products.PloneTestCase.setup import USELAYER
from Products.PloneTestCase.setup import Z3INTERFACES
from Products.PloneTestCase.setup import portal_name
from Products.PloneTestCase.setup import portal_owner
from Products.PloneTestCase.setup import default_policy
from Products.PloneTestCase.setup import default_products
from Products.PloneTestCase.setup import default_base_profile
from Products.PloneTestCase.setup import default_extension_profiles
from Products.PloneTestCase.setup import default_user
from Products.PloneTestCase.setup import default_password

from Products.PloneTestCase.setup import setupPloneSite

from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase


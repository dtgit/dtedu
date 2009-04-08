#
# CMFTestCase API
#

# $Id: ctc.py 44425 2007-06-23 19:58:46Z shh42 $

from Testing.ZopeTestCase import hasProduct
from Testing.ZopeTestCase import installProduct

try:
    from Testing.ZopeTestCase import hasPackage
    from Testing.ZopeTestCase import installPackage
except ImportError:
    pass

from Testing.ZopeTestCase import Sandboxed
from Testing.ZopeTestCase import Functional

from Products.CMFTestCase import utils
from Products.CMFTestCase.utils import *

from Products.CMFTestCase import setup
from Products.CMFTestCase.setup import CMF15
from Products.CMFTestCase.setup import CMF16
from Products.CMFTestCase.setup import CMF20
from Products.CMFTestCase.setup import CMF21
from Products.CMFTestCase.setup import USELAYER
from Products.CMFTestCase.setup import Z3INTERFACES
from Products.CMFTestCase.setup import portal_name
from Products.CMFTestCase.setup import portal_owner
from Products.CMFTestCase.setup import default_products
from Products.CMFTestCase.setup import default_base_profile
from Products.CMFTestCase.setup import default_extension_profiles
from Products.CMFTestCase.setup import default_user
from Products.CMFTestCase.setup import default_password

from Products.CMFTestCase.setup import setupCMFSite

from Products.CMFTestCase.CMFTestCase import CMFTestCase
from Products.CMFTestCase.CMFTestCase import FunctionalTestCase


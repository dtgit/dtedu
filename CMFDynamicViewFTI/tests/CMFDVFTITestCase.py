#
# CMFDVFTITestCase
#

from Products.CMFTestCase.ctc import *

from Products.CMFCore.interfaces import ISiteRoot
from Products.GenericSetup import EXTENSION, profile_registry

installProduct('CMFDynamicViewFTI')

profile_registry.registerProfile('CMFDVFTI_sampletypes',
    'CMFDynamicViewFTI Sample Content Types',
    'Extension profile including CMFDVFTI sample content types',
    'profiles/sample_types',
    'CMFDynamicViewFTI',
    EXTENSION,
    for_=ISiteRoot)

setupCMFSite(extension_profiles=['CMFDynamicViewFTI:CMFDVFTI_sampletypes'])

class CMFDVFTITestCase(CMFTestCase):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """

class FunctionalTestCase(Functional, CMFTestCase):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """

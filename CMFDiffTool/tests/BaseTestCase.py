# BaseTestCase

from Products.CMFTestCase.ctc import *

installProduct('CMFDiffTool')

setupCMFSite(extension_profiles=['Products.CMFDiffTool:CMFDiffTool'])

class BaseTestCase(CMFTestCase):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """

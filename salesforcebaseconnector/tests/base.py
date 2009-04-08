"""Base class for integration tests, based on ZopeTestCase and CMFTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox CMFSite site with the appropriate
products installed.
"""

from Testing import ZopeTestCase
from Products.CMFTestCase import CMFTestCase

# Let Zope know about the two products we require above-and-beyond a basic CMFSite install
ZopeTestCase.installProduct('salesforcebaseconnector')

CMFTestCase.setupCMFSite()

class SalesforceBaseConnectorTestCase(CMFTestCase.CMFTestCase):
    """Base class for integration tests for the 'salesforcebaseconnector' product.
    """
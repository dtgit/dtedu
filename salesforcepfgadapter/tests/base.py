# Import the base test case classes
from Testing import ZopeTestCase as ztc
from Products.CMFPlone.tests import PloneTestCase

# These must install cleanly, ZopeTestCase will take care of the others
ztc.installProduct('PloneFormGen')
ztc.installProduct('DataGridField')
ztc.installProduct('salesforcebaseconnector')
ztc.installProduct('salesforcepfgadapter')

# Set up the Plone site used for the test fixture. The PRODUCTS are the products
# to install in the Plone site (as opposed to the products defined above, which
# are all products available to Zope in the test fixture)
PRODUCTS = ['salesforcepfgadapter']

PloneTestCase.setupPloneSite(products=PRODUCTS)

class SalesforcePFGAdapterTestCase(PloneTestCase.PloneTestCase):
    """Base class for integration tests for the 'salesforcepfgadapter' product. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """

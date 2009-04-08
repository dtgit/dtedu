# Define a common SimpleAttachmentTestCase base class for use in all
# SimpleAttachment tests

# Import the base test case classes
from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase

# Make ZopeTestCase aware of the standard products
ZopeTestCase.installProduct('SimpleAttachment')

# Set up the Plone site used for the test fixture. The PRODUCTS are the products
# to install in the Plone site (as opposed to the products defined above, which
# are all products available to Zope in the test fixture)
PRODUCTS = ['SimpleAttachment']
PloneTestCase.setupPloneSite(products=PRODUCTS)

class SimpleAttachmentTestCase(PloneTestCase.PloneTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()

    # You may wish to define additional helper methods
    # here that will be available in all tests.

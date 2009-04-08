from base import SalesforceBaseConnectorTestCase
from Products.CMFCore.utils import getToolByName
import datetime
from DateTime import DateTime
from Products.salesforcebaseconnector.utils import DateTime2datetime

# be sure to set USERNAME/PASSWORD for test config
from Products.salesforcebaseconnector.tests import sfconfig

class TestSBCUtils(SalesforceBaseConnectorTestCase):
    def afterSetUp(self):
        """Pre-test case setup"""
        
        # add, but don't configure, since that's the point of our tests
        self.portal.manage_addProduct['salesforcebaseconnector'].manage_addTool('Salesforce Base Connector', None)
        self.toolbox = getToolByName(self.portal, "portal_salesforcebaseconnector")
    
    def testDateTime2datetime(self):
        # datetime comes back unscathed
        sample_time = datetime.datetime(2008, 2, 1)
        self.assertEqual(sample_time, DateTime2datetime(sample_time))
        self.assertRaises(ValueError, DateTime2datetime, 'some string')
        self.failUnless(isinstance(DateTime2datetime(DateTime()), datetime.datetime))
    


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSBCUtils))
    return suite


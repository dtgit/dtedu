# Migration tests specific to Salesforce adapter
#

import os, sys, email
import transaction
from Products.salesforcebaseconnector.tests import sfconfig   # get login/pw
from Products.salesforcepfgadapter.migrations.migrateUpTo10rc1 import Migration
from Products.salesforcepfgadapter.Extensions.Install import _productNeedsMigrationTo10RC1

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFCore.utils import getToolByName

from Products.salesforcepfgadapter.tests import base

class TestProductMigration(base.SalesforcePFGAdapterTestCase):
    """ ensure that our product migrates correctly from version to version 
        with thanks to CMFPlone/tests/testMigrations.py for numerous examples.
    """
    
    def afterSetUp(self):
        self.types   = getToolByName(self.portal, 'portal_types')
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        self.qi      = getToolByName(self.portal, 'portal_quickinstaller')
        
        self.portal.manage_addProduct['salesforcebaseconnector'].manage_addTool('Salesforce Base Connector', None)
        self.salesforce = getToolByName(self.portal, "portal_salesforcebaseconnector")
        self.salesforce.setCredentials(sfconfig.USERNAME, sfconfig.PASSWORD)
        self.migration = Migration(self.portal, [])
    
    def testTypeIndexRebuiltViaReinstallationTestsMigrationTo10rc1(self):
        # make a form folder
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
        
        # force set the portal's version
        self.qi.salesforcepfgadapter.installedversion = '1.0alpha1'
        
        # change the type name, so an outdated version gets created
        adapter = self.types.get('SalesforcePFGAdapter')
        adapter.title = 'Unmigrated'
        
        # make an adapter
        self.ff1.invokeFactory('SalesforcePFGAdapter', 'salesforceadapter')
        self.ff1.salesforceadapter.reindexObject()
        
        # assert that misnamed type exists in Type index, and the 
        # meta/portal type remains as expected
        self.failUnless("SalesforcePFGAdapter" in self.catalog.uniqueValuesFor('portal_type'))
        self.failUnless("SalesforcePFGAdapter" in self.catalog.uniqueValuesFor('meta_type'))
        self.failUnless("Unmigrated" in self.catalog.uniqueValuesFor('Type'))
        
        # quickinstall
        self.qi.reinstallProducts(['salesforcepfgadapter',])
        
        # our migration is happen
        self.failUnless("SalesforcePFGAdapter" in self.catalog.uniqueValuesFor('portal_type'))
        self.failUnless("SalesforcePFGAdapter" in self.catalog.uniqueValuesFor('meta_type'))
        self.failUnless("Salesforce Adapter" in self.catalog.uniqueValuesFor('Type'))
    
    def testDataTypeForOnInstanceFieldsForSFObjectTypeMigratedTo10rc1(self):
        """prior to version 1.0rc1, we were instantiating the adapter with 
           a private attribute, _fieldsForSFObjectType, as a list.  In a nutshell,
           we were populating this with a list of the fields for the chosen SFObject
           and threw away a bunch of extra field information provided by Salesforce.
           In order to mark certain fields as required in the UI, we needed to change
           the data structure and store more information locally.  This caused breakage
           in pre-modification adapter instances and our migration regenerates the value stored.
        """
        
        # make a form folder
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
        
        # force set the portal's version
        self.qi.salesforcepfgadapter.installedversion = '1.0alpha1'
        
        # create an adapter
        self.ff1.invokeFactory('SalesforcePFGAdapter', 'salesforce')
        
        # we brute force our attribute to the previous data structure
        self.ff1.salesforce._fieldsForSFObjectType = []
        
        # a list has no call for items, thus the attribute error
        self.assertRaises(AttributeError, self.ff1.salesforce.buildSFFieldOptionList)
        
        # quickinstall
        self.qi.reinstallProducts(['salesforcepfgadapter',])
        
        # make sure our migration has resolved the situation
        self.assertEqual(type(dict()), type(self.ff1.salesforce._fieldsForSFObjectType))
    
    def testMigrationTo10rc1RequiredForVersions(self):
        versionMigrationNeededMapping = {
            '1.0alpha1':True,
            '1.0alpha2':True,
            '1.0alpha3':True,
            '1.0alpha1 (svn/unreleased)':True,
            '1.0alpha1 (SVN/UNRELEASED)':False,
            'Some Bogus Version':False,
            '1.0rc1':False,
            '1.0rc2':False,
            '5.0':False,
        }
        
        for k,v in versionMigrationNeededMapping.items():
            self.qi.salesforcepfgadapter.installedversion = k
            
            self.assertEqual(v, _productNeedsMigrationTo10RC1(self.qi),
                "Version %s received an incorrect version migration status response" % k)
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductMigration))
    return suite

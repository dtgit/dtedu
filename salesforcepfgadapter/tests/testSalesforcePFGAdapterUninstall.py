# Integration tests specific to Salesforce adapter
#

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.salesforcepfgadapter.tests import base

from Products.CMFCore.utils import getToolByName

class TestProductUninstallation(base.SalesforcePFGAdapterTestCase):
    """ ensure that our product installs correctly """

    def afterSetUp(self):
        self.types      = self.portal.portal_types
        self.properties = self.portal.portal_properties
        self.factory    = self.portal.portal_factory
        self.skins      = self.portal.portal_skins
        self.qi         = self.portal.portal_quickinstaller
        self.workflow   = self.portal.portal_workflow

        self.adapterTypes = (
            'SalesforcePFGAdapter',
        )
        
        self.metaTypes = self.adapterTypes
        
        # uninstall our product
        if self.qi.isProductInstalled('salesforcepfgadapter'):
            self.qi.uninstallProducts(products=['salesforcepfgadapter',])
    
    def testDependenciesStillInstalled(self):
        """Just because someone chooses to uninstall the salesforcepfgadapter
           product doesn't mean they want to remove it's dependencies.  This
           should be done manually in addition to uninstalling salesforcepfgadapter.
        """
        DEPENDENCIES = ['PloneFormGen',]
        
        for depend in DEPENDENCIES:
            self.failUnless(self.qi.isProductInstalled(depend),
                "Dependency product %s is not already installed" % depend)    
    
    def testQIDeemsProductUninstalled(self):
        """Make sure the product is uninstalled in the eyes of the portal_quickinstaller"""
        self.failIf(self.qi.isProductInstalled('salesforcepfgadapter'))
    
    def testAdapterTypeNotRegisteredOnUninstall(self):
        for t in self.metaTypes:
            self.failIf(t in self.types.objectIds(),
                "Type %s is still registered with the types tool after uninstallation." % t)

    def testFactoryTypesRemovedOnUninstall(self):
        for t in self.metaTypes:
            self.failIf(t in self.factory.getFactoryTypes(),
                "Type %s is still a factory type after uninstallation." % t)

    def testTypesNotSearchedRemovedOnUninstall(self):
        types_not_searched = self.properties.site_properties.getProperty('types_not_searched')
        for t in self.metaTypes:
            self.failIf(t in types_not_searched,
                "Type %s is still in the types_not_searched list after uninstallation" % t)

    def testTypesNotListedRemovedOnUninstall(self):
        metaTypesNotToList  = self.properties.navtree_properties.getProperty('metaTypesNotToList')
        for t in self.metaTypes:
            self.failIf(t in metaTypesNotToList,
                "Type %s is still in the list of metaTypesNotToList after uninstallation" % t)

    def testMetaTypesAllowedInFormFolderRemovedOnUninstall(self):
        allowedTypes = self.types.FormFolder.allowed_content_types
        for t in self.metaTypes:
            self.failIf(t in allowedTypes,
                "Type %s is still listed as addable to the Form Folder after uninstallation" % t)
    
    def testSkinsRemovedOnUninstall(self):
        """Our all important skin layer(s) should be registered with the site."""
        prodSkins = ('salesforcepfgadapter_images',)

        for prodSkin in prodSkins:
            self.failIf(prodSkin in self.skins.objectIds(),
                "The skin %s is still registered with the skins tool after uninstallation" % prodSkin)

    def testSkinLayersRemovedOnUninstall(self):
        """We need our product's skin directories to show up below custom as one of the called
           upon layers of our skin's properties
        """
        product_layers = ('salesforcepfgadapter_images',)
        
        for selection, layers in self.skins.getSkinPaths():
            for specific_layer in product_layers:
                self.failIf(specific_layer in layers, "The %s layer \
                    still appears in the layers of Plone's %s skin after uninstall" % (specific_layer,selection))
    
    def testWorkflowToolNoLongerMaintainsWorkflowChainForRemovedType(self):
        for t in self.metaTypes:
            self.failIf(self.workflow.getChainForPortalType(t))
    
    def testProductInstallsUninstallsCorrectly(self):
        # ensure that we can install/uninstall code correctly
        # this helps ensure that we aren't doing things like
        # deleting/adding property sheet items out of order and
        # with proper fallback -- plus, it helps us get better 
        # output in our --coverage results :)
        
        # ensure installable after uninstall
        self.failUnless(self.qi.isProductInstallable('salesforcepfgadapter'))
        self.qi.installProducts(products=['salesforcepfgadapter',])
        
        # uninstall product
        self.qi.uninstallProducts(products=['salesforcepfgadapter',])
        self.failUnless(self.qi.isProductInstallable('salesforcepfgadapter'))
        
    
if  __name__ == '__main__':
    framework()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductUninstallation))
    return suite

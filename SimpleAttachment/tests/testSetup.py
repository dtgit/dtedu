from Products.SimpleAttachment.tests import base

class TestInstallation(base.SimpleAttachmentTestCase):
    """Ensure product is properly installed"""

    def afterSetUp(self):
        self.css        = self.portal.portal_css
        self.kupu       = self.portal.kupu_library_tool
        self.skins      = self.portal.portal_skins
        self.types      = self.portal.portal_types
        self.factory    = self.portal.portal_factory
        self.workflow   = self.portal.portal_workflow
        self.properties = self.portal.portal_properties

        self.metaTypes = ('ImageAttachment', 'FileAttachment')

    def testSkinLayersInstalled(self):
        self.failUnless('attachment_widgets' in self.skins.objectIds())
        self.failUnless('simpleattachment' in self.skins.objectIds())
        
    def testTypesInstalled(self):
        for t in self.metaTypes:
            self.failUnless(t in self.types.objectIds())

    def testTypesNotSearched(self):
        types_not_searched = self.properties.site_properties.getProperty('types_not_searched')
        self.failUnless('FileAttachment' in types_not_searched)
        self.failUnless('ImageAttachment' in types_not_searched)

    def testTypesUseViewActionInListings(self):
        typesUseViewActionInListings = self.properties.site_properties.getProperty('typesUseViewActionInListings')
        self.failUnless('FileAttachment' in typesUseViewActionInListings)
        self.failUnless('ImageAttachment' in typesUseViewActionInListings)

    def testAttachmentsHaveNoWorkflow(self):
        self.assertEqual(self.workflow.getChainForPortalType('FileAttachment'), ())
        self.assertEqual(self.workflow.getChainForPortalType('ImageAttachment'), ())
    
    def testKupuResources(self):
        linkable = self.kupu.getPortalTypesForResourceType('linkable')
        mediaobject = self.kupu.getPortalTypesForResourceType('mediaobject')
        self.failUnless('FileAttachment' in linkable)
        self.failUnless('ImageAttachment' in linkable)
        self.failUnless('ImageAttachment' in mediaobject)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstallation))
    return suite


from Products.CMFDynamicViewFTI.tests import CMFDVFTITestCase

import zope.component 
import zope.publisher.browser

from Products.CMFCore.utils import getToolByName

from Products.CMFDynamicViewFTI.interfaces import ISelectableBrowserDefault
from Products.CMFDynamicViewFTI.interfaces import IBrowserDefault
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Interface.Verify import verifyClass

class DummyFolder(BrowserDefaultMixin):

    def getTypeInfo(self):
        return self.fti

class IDummy(zope.interface.Interface):
    """ marker interface for a zope 3 view """

class BrowserView(zope.publisher.browser.BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request   

class TestBrowserDefault(CMFDVFTITestCase.CMFDVFTITestCase):

    def test_doesImplementISelectableBrowserDefault(self):
        iface = ISelectableBrowserDefault
        self.failUnless(iface.isImplementedByInstancesOf(BrowserDefaultMixin))
        self.failUnless(verifyClass(iface, BrowserDefaultMixin))

    def test_extendsInterface(self):
        self.failUnless(ISelectableBrowserDefault.extends(IBrowserDefault))

class TestAvailableLayouts(CMFDVFTITestCase.CMFDVFTITestCase):

    def afterSetUp(self):
        self.types = getToolByName(self.portal, 'portal_types')

        self.dfolder = DummyFolder()
        self.dfolder.fti = self.types['DynFolder']

        from Products.Five import zcml
        import plone.app.contentmenu
        import Products.CMFDynamicViewFTI.tests
        zcml.load_config('configure.zcml', plone.app.contentmenu)
        zcml.load_config('browserdefault.zcml', 
                         Products.CMFDynamicViewFTI.tests)
        
    def test_Zope3View(self):
        dfolder = self.dfolder
        dfolder.layout = 'zope3_view'
        dfolder.REQUEST = zope.publisher.browser.TestRequest()
        view_methods = dfolder.getAvailableLayouts()
        view_ids = [ view_id for view_id, foo in view_methods ]
        self.failIf(dfolder.layout in view_ids)
        
        # Mark the object with interface connected to the zope 3 view
        zope.interface.directlyProvides(dfolder, IDummy)
        view_methods = dfolder.getAvailableLayouts()
        view_ids = [ view_id for view_id, foo in view_methods ]
        self.failIf(dfolder.layout not in view_ids)
        
    def test_Zope3ViewTitle(self):
        dfolder = self.dfolder
        dfolder.layout = 'zope3_view'
        dfolder.REQUEST = zope.publisher.browser.TestRequest()
        zope.interface.directlyProvides(dfolder, IDummy)
        view_methods = dfolder.getAvailableLayouts()
        
        for id, title in view_methods:
            if id == dfolder.layout:
                self.assertEqual(title, 'Zope3 Test View')
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBrowserDefault))
    suite.addTest(makeSuite(TestAvailableLayouts))    
    return suite

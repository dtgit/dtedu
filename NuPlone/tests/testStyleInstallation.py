#
# Unit Tests for the style install and uninstall methods
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase

# CHANGE 'NuPlone' to your product name in the following lines
from Products.NuPlone.config import *
from Products.NuPlone.Extensions.utils import getSkinsFolderNames
PROJECTNAME = 'NuPlone'

PloneTestCase.installProduct(PROJECTNAME)
PloneTestCase.setupPloneSite(products=[PROJECTNAME])

class testSkinsTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.portal, 'portal_skins')

    def testSkinSelectionCreated(self):
        """Test if a new skin exists in portal_skins."""
        for skin_selection in SKINSELECTIONS:
            self.failUnless(
                skin_selection['name'] in self.tool.getSkinSelections())

    def testSkinPaths(self):
        """Test if the skin layers in the new skin were correctly added."""
        skinsfoldernames = getSkinsFolderNames(GLOBALS)
        skins_dict = {}
        for skin in SKINSELECTIONS:
            skins_dict[skin['name']] = skin.get('layers', skinsfoldernames)
        for selection, layers in self.tool.getSkinPaths():
            if skins_dict.has_key(selection):
                for specific_layer in skins_dict[selection]:
                    self.failUnless(specific_layer in layers)
            else:
                for foldername in skinsfoldernames:
                    self.failIf(foldername in layers)

    def testSkinSelection(self):
        """Test if the new skin was selected as default one."""
        if SELECTSKIN:
            self.assertEqual(self.tool.getDefaultSkin(), DEFAULTSKIN)

    def testSkinFlexibility(self):
        """Test if the users can choose their skin."""
        self.assertEqual(self.tool.getAllowAny(), ALLOWSELECTION)

    def testCookiePersistance(self):
        """Test if the skin choice is peristant between sessions."""
        self.assertEqual(bool(self.tool.getCookiePersistence()),
                                                        PERSISTENTCOOKIE)

class testResourceRegistrations(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.qitool      = getattr(self.portal, 'portal_quickinstaller')
        self.csstool     = getattr(self.portal, 'portal_css')
        self.jstool      = getattr(self.portal, 'portal_javascripts')
        product_settings = getattr(self.qitool, PROJECTNAME)
        self.stylesheets = product_settings.resources_css
        self.javascripts = product_settings.resources_js

    def testStylesheetsInstalled(self):
        """Test if new stylesheets were added to portal_css."""
        stylesheetids = self.csstool.getResourceIds()
        for css in STYLESHEETS:
            self.failUnless(css['id'] in stylesheetids)

    def testStylesheetProperties(self):
        """Test if new stylesheets have correct parameters."""
        for config in STYLESHEETS:
            res = self.csstool.getResource(config['id'])
            for key in [key for key in config.keys() if key != 'id']:
                self.assertEqual(res._data[key], config[key])

    def testStylesheetsUpdated(self):
        """Test if existing stylesheets were correctly updated."""
        for config in [c for c in STYLESHEETS
                       if c['id'] not in self.stylesheets]:
            resource = self.csstool.getResource(config['id'])
            for key in [k for k in config.keys() if k != 'id']:
                self.failUnless(resource._data.has_key('original_'+key))

    def testJavascriptsInstalled(self):
        """Test if new javascripts were added to portal_javascripts."""
        javascriptids = self.jstool.getResourceIds()
        for js in JAVASCRIPTS:
            self.failUnless(js['id'] in javascriptids)

    def testMemberStylesheetProperties(self):
        """Test if new javascripts have correct parameters."""
        for config in JAVASCRIPTS:
            res = self.jstool.getResource(config['id'])
            for key in [key for key in config.keys() if key != 'id']:
                self.assertEqual(res._data[key], config[key])

    def testJavascriptsUpdated(self):
        """Test if existing javascripts were correctly updated."""
        for config in [c for c in JAVASCRIPTS
                       if c['id'] not in self.javascripts]:
            resource = self.jstool.getResource(config['id'])
            for key in [k for k in config.keys() if k != 'id']:
                self.failUnless(resource._data.has_key('original_'+key))

class testDisplayViewsRegistration(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.ttool = getattr(self.portal, 'portal_types')

    def testDisplayViewsRegistered(self):
        """Test if additional display views were added to specified types."""
        if DISPLAY_VIEWS:
            for pt, views in DISPLAY_VIEWS.items():
                FTI = getattr(self.ttool, pt)
                registered_views = FTI.view_methods
                for view in views:
                    self.failUnless(view in registered_views)


class testUninstall(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        """Test if ."""
        self.qitool      = getattr(self.portal, 'portal_quickinstaller')
        self.skinstool   = getattr(self.portal, 'portal_skins')
        self.csstool     = getattr(self.portal, 'portal_css')
        self.jstool      = getattr(self.portal, 'portal_javascripts')
        product_settings = getattr(self.qitool, PROJECTNAME)
        self.stylesheets = product_settings.resources_css
        self.javascripts = product_settings.resources_js
        self.qitool.uninstallProducts(products=[PROJECTNAME])
        self.ttool = getattr(self.portal, 'portal_types')

    def testProductUninstalled(self):
        """Test if the product was uninstalled."""
        self.failIf(self.qitool.isProductInstalled(PROJECTNAME))

    def testSkinSelectionDeleted(self):
        """Test if the skin selection was removed from portal_skins."""
        skin_selections = self.skinstool.getSkinSelections()
        for skin in SKINSELECTIONS:
            self.failIf(skin['name'] in skin_selections)

    def testDefaultSkinChanged(self):
        """Test if default skin is back to old value or default Plone."""
        default_skin = self.skinstool.getDefaultSkin()
        if RESETSKINTOOL:
            self.assertEqual(default_skin, 'Plone Default')
        else:
            if DEFAULTSKIN:
                for skin in SKINSELECTIONS:
                    if skin['name'] == DEFAULTSKIN:
                        self.assertEqual(default_skin, skin['base'])
            else:
                self.assertEqual(default_skin, SKINSELECTIONS[0]['base'])

    def testResetSkinFlexibility(self):
        """Test if the users still can choose their skin."""
        allow_any = self.skinstool.getAllowAny()
        if RESETSKINTOOL:
            self.failIf(allow_any)
        else:
            self.assertEqual(allow_any, ALLOWSELECTION)

    def testResetCookiePersistance(self):
        """Test if the skin choice is still peristant between sessions."""
        cookie_peristence = self.skinstool.getCookiePersistence()
        if RESETSKINTOOL:
            self.failIf(cookie_peristence)
        else:
            self.assertEqual(cookie_peristence, PERSISTENTCOOKIE)

    def testStylesheetsUninstalled(self):
        """Test if added stylesheets were removed from portal_css."""
        resourceids = self.csstool.getResourceIds()
        for css in self.stylesheets:
            self.failIf(css in resourceids)

    def testResetDefaultStylesheets(self):
        """Test if values were reverted in existing stylesheets."""
        for config in [c for c in STYLESHEETS
                       if c['id'] not in self.stylesheets]:
            resource = self.csstool.getResource(config['id'])
            for key in [k for k in config.keys() if k != 'id']:
                self.failIf(resource._data.has_key('original_'+key))

    def testJavascriptsUninstalled(self):
        """Test if added javascripts were removed from portal_js."""
        resourceids = self.jstool.getResourceIds()
        for js in self.javascripts:
            self.failIf(js in resourceids)

    def testResetDefaultJavascripts(self):
        """Test if values were reverted in existing javascripts."""
        for config in [c for c in JAVASCRIPTS
                       if c['id'] not in self.javascripts]:
            resource = self.jstool.getResource(config['id'])
            for key in [k for k in config.keys() if k != 'id']:
                self.failIf(resource._data.has_key('original_'+key))

    def testDisplayViewsUnregistered(self):
        """Make sure additional Display Views were removed"""
        if DISPLAY_VIEWS:
            for pt, views in DISPLAY_VIEWS.items():
                FTI = getattr(self.ttool, pt)
                registered_views = FTI.view_methods
                for view in views:
                    self.failIf(view in registered_views)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(testSkinsTool))
        suite.addTest(unittest.makeSuite(testResourceRegistrations))
        suite.addTest(unittest.makeSuite(testDisplayViewsRegistration))
        suite.addTest(unittest.makeSuite(testUninstall))
        return suite
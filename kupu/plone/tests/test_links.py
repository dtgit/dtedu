##############################################################################
#
# Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Tests for the link checking and migration code"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from kuputestcase import *
from Products.kupu.plone.html2captioned import Migration

class TestLinkCode(KupuTestCase):
    """Test the link checking code"""

    def test_relative(self):
        self.setup_content()
        migrator = Migration(self.kupu)
        portal = self.portal
        base = portal.folder.sub2.delta.absolute_url()
        path = '../alpha'
        expected = ('internal', portal.folder.alpha.UID(), path, '')
        self.assertEquals(expected, migrator.classifyLink(path, base))

    def test_external(self):
        self.setup_content()
        migrator = Migration(self.kupu)
        portal = self.portal
        base = portal.folder.sub2.delta.absolute_url()
        path = 'mailto:me@nowhere'
        expected = ('external', None, path, '')
        self.assertEquals(expected, migrator.classifyLink(path, base))

    def test_localexternal(self):
        self.setup_content()
        migrator = Migration(self.kupu)
        portal = self.portal
        base = portal.folder.sub2.delta.absolute_url()
        path = 'http://nohost/plone/folder/alpha'
        expected = ('internal', portal.folder.alpha.UID(), '../alpha', '')
        self.assertEquals(expected, migrator.classifyLink(path, base))

    def test_abspath(self):
        self.setup_content()
        migrator = Migration(self.kupu)
        portal = self.portal
        base = portal.folder.alpha.absolute_url()
        path = '/plone/folder/beta'
        expected = ('internal', portal.folder.beta.UID(), 'beta', '')
        self.assertEquals(expected, migrator.classifyLink(path, base))

    def test_anchor(self):
        self.setup_content()
        migrator = Migration(self.kupu)
        portal = self.portal
        base = portal.folder.alpha.absolute_url()
        path = '#fred'
        expected = ('internal', None, '', path)
        self.assertEquals(expected, migrator.classifyLink(path, base))

    def test_redundant(self):
        self.setup_content()
        migrator = Migration(self.kupu)
        portal = self.portal
        base = portal.folder.alpha.absolute_url()
        path = 'alpha#fred'
        expected = ('internal', None, '', '#fred')
        self.assertEquals(expected, migrator.classifyLink(path, base))

    def test_bad_portal_factory(self):
        # Some version of kupu wrongly inserted jumplinks to
        # portal_factory. Check these get cleaned.
        self.setup_content()
        migrator = Migration(self.kupu)
        portal = self.portal
        base = portal.folder.alpha.absolute_url()
        path = 'portal_factory#fred'
        expected = ('internal', None, '', '#fred')
        self.assertEquals(expected, migrator.classifyLink(path, base))

    def test_dot(self):
        self.setup_content()
        migrator = Migration(self.kupu)
        portal = self.portal
        base = portal.folder.alpha.absolute_url()
        path = '.'
        expected = ('internal', portal.folder.UID(), path, '')
        self.assertEquals(expected, migrator.classifyLink(path, base))

    def test_resolveuid(self):
        self.setup_content()
        migrator = Migration(self.kupu)
        portal = self.portal
        base = portal.folder.alpha.absolute_url()
        path = 'resolveuid/' + portal.folder.beta.UID()
        expected = ('internal', portal.folder.beta.UID(), 'beta', '')
        self.assertEquals(expected, migrator.classifyLink(path, base))

    def test_resolveuidEmbedded(self):
        self.setup_content()
        migrator = Migration(self.kupu)
        portal = self.portal
        base = portal.folder.alpha.absolute_url()
        path = 'wibble/resolveuid/' + portal.folder.beta.UID() + '#fragment'
        expected = ('internal', portal.folder.beta.UID(), 'beta', '#fragment')
        self.assertEquals(expected, migrator.classifyLink(path, base))

    def test_badlink(self):
        self.setup_content()
        migrator = Migration(self.kupu)
        portal = self.portal
        base = portal.folder.alpha.absolute_url()
        path = 'wibble'
        expected = ('bad', None, path, '')
        self.assertEquals(expected, migrator.classifyLink(path, base))

    def test_image(self):
        self.setup_content()
        migrator = Migration(self.kupu)
        migrator.initImageSizes()
        portal = self.portal
        base = portal.folder.alpha.absolute_url()
        path = 'gamma/image_thumb'
        expected = ('internal', portal.folder.gamma.UID(), 'gamma', '/image_thumb')
        self.assertEquals(expected, migrator.classifyLink(path, base))

    def test_image2(self):
        self.setup_content()
        migrator = Migration(self.kupu)
        portal = self.portal
        base = portal.folder.alpha.absolute_url()
        path = 'resolveuid/'+portal.folder.gamma.UID()+'/image_icon'
        expected = ('internal', portal.folder.gamma.UID(), 'gamma', '/image_icon')
        self.assertEquals(expected, migrator.classifyLink(path, base))

        
if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestLinkCode))
        return suite

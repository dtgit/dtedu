##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for URLTool module.

$Id: test_URLTool.py 77186 2007-06-28 19:06:19Z yuppie $
"""

import unittest
import Testing

from zope.component import getSiteManager
from zope.testing.cleanup import cleanUp

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.dummy import DummyFolder
from Products.CMFCore.tests.base.dummy import DummySite


class URLToolTests(unittest.TestCase):

    def setUp(self):
        self.site = DummySite(id='foo')
        sm = getSiteManager()
        sm.registerUtility(self.site, ISiteRoot)

    def tearDown(self):
        cleanUp()

    def _makeOne(self, *args, **kw):
        from Products.CMFCore.URLTool import URLTool

        url_tool = URLTool(*args, **kw)
        return url_tool.__of__( self.site )

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider
        from Products.CMFCore.interfaces.portal_url \
                import portal_url as IURLTool
        from Products.CMFCore.URLTool import URLTool

        verifyClass(IActionProvider, URLTool)
        verifyClass(IURLTool, URLTool)

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFCore.interfaces import IActionProvider
        from Products.CMFCore.interfaces import IURLTool
        from Products.CMFCore.URLTool import URLTool

        verifyClass(IActionProvider, URLTool)
        verifyClass(IURLTool, URLTool)

    def test_portal_methods(self):
        url_tool = self._makeOne()
        self.assertEqual( url_tool()
                        , 'http://www.foobar.com/bar/foo' )
        self.assertEqual( url_tool.getPortalObject()
                        , self.site )
        self.assertEqual( url_tool.getPortalPath()
                        , '/bar/foo' )

    def test_content_methods(self):
        url_tool = self._makeOne()
        self.site._setObject( 'folder', DummyFolder(id='buz') )
        self.site.folder._setObject( 'item', DummyContent(id='qux.html') )
        obj = self.site.folder.item
        self.assertEqual( url_tool.getRelativeContentPath(obj)
                        , ('buz', 'qux.html') )
        self.assertEqual( url_tool.getRelativeContentURL(obj)
                        , 'buz/qux.html' )
        self.assertEqual( url_tool.getRelativeUrl(obj)
                        , 'buz/qux.html' )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( URLToolTests ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

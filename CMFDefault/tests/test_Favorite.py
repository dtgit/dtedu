##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for Favorites.

$Id: test_Favorite.py 77113 2007-06-26 20:36:26Z yuppie $
"""

import unittest
import Testing

from zope.component import getSiteManager
from zope.testing.cleanup import cleanUp

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.testing import ConformsToContent
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool


class FavoriteTests(ConformsToContent, unittest.TestCase):

    def _getTargetClass(self):
        from Products.CMFDefault.Favorite import Favorite

        return Favorite

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def setUp(self):
        sm = getSiteManager()
        self.site = DummySite('site')
        sm.registerUtility(self.site, ISiteRoot)
        self.site._setObject( 'portal_membership', DummyTool() )
        self.site._setObject( 'portal_url', DummyTool() )

    def tearDown(self):
        cleanUp()

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFDefault.interfaces import IFavorite
        from Products.CMFDefault.interfaces import ILink
        from Products.CMFDefault.interfaces import IMutableFavorite
        from Products.CMFDefault.interfaces import IMutableLink

        verifyClass(IFavorite, self._getTargetClass())
        verifyClass(ILink, self._getTargetClass())
        verifyClass(IMutableFavorite, self._getTargetClass())
        verifyClass(IMutableLink, self._getTargetClass())

    def test_Empty( self ):
        utool = self.site.portal_url
        f = self.site._setObject('foo', self._makeOne('foo'))

        self.assertEqual( f.getId(), 'foo' )
        self.assertEqual( f.Title(), '' )
        self.assertEqual( f.Description(), '' )
        self.assertEqual( f.getRemoteUrl(), utool.root )
        self.assertEqual( f.getObject(), self.site )
        self.assertEqual( f.getIcon(), self.site.getIcon() )
        self.assertEqual( f.getIcon(1), self.site.getIcon(1) )

    def test_CtorArgs( self ):
        utool = self.site.portal_url
        self.assertEqual( self._makeOne( 'foo'
                                       , title='Title'
                                       ).Title(), 'Title' )

        self.assertEqual( self._makeOne( 'bar'
                                       , description='Description'
                                       ).Description(), 'Description' )

        baz = self.site._setObject('foo',
                                self._makeOne('baz', remote_url='portal_url'))
        self.assertEqual( baz.getObject(), utool )
        self.assertEqual( baz.getRemoteUrl()
                        , '%s/portal_url' % utool.root )
        self.assertEqual( baz.getIcon(), utool.getIcon() )

    def test_edit( self ):
        utool = self.site.portal_url
        f = self.site._setObject('foo', self._makeOne('foo'))
        f.edit( 'portal_url' )
        self.assertEqual( f.getObject(), utool )
        self.assertEqual( f.getRemoteUrl()
                        , '%s/portal_url' % utool.root )
        self.assertEqual( f.getIcon(), utool.getIcon() )

    def test_editEmpty( self ):
        utool = self.site.portal_url
        f = self.site._setObject('gnnn', self._makeOne('gnnn'))
        f.edit( '' )
        self.assertEqual( f.getObject(), self.site )
        self.assertEqual( f.getRemoteUrl(), utool.root )
        self.assertEqual( f.getIcon(), self.site.getIcon() )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FavoriteTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

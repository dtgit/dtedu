#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
"""

__author__ = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase, atctftestcase
from Products.ATContentTypes.config import TOOLNAME
from Products.ATContentTypes.interfaces import IATCTTool
from Interface.Verify import verifyObject
from Products.CMFCore.utils import getToolByName

# z3 imports
from Products.ATContentTypes.interface import IATCTTool as Z3IATCTTool
from zope.interface.verify import verifyObject as Z3verifyObject

tests = []

class TestTool(atcttestcase.ATCTSiteTestCase):

    def afterSetUp(self):
        self.tool = getToolByName(self.portal, TOOLNAME)
        
    def test_interface(self):
        t = self.tool
        self.failUnless(IATCTTool.isImplementedBy(t))
        self.failUnless(verifyObject(IATCTTool, t))

    def test_Z3interface(self):
        t = self.tool
        iface = Z3IATCTTool
        self.failUnless(Z3verifyObject(iface, t))
        
    def test_names(self):
        t = self.tool
        self.failUnlessEqual(t.meta_type, 'ATCT Tool')
        self.failUnlessEqual(t.getId(), TOOLNAME)
        self.failUnlessEqual(t.title, 'ATContentTypes Tool')

tests.append(TestTool)


class TestATCTToolFunctional(atctftestcase.IntegrationTestCase):
    
    zmi_tabs = ('manage_imageScales', 'manage_overview', )
    
    def setupTestObject(self):
        self.obj_id = TOOLNAME
        self.obj = getToolByName(self.portal, TOOLNAME)
        self.obj_url = self.obj.absolute_url()
        self.obj_path = '/%s' % self.obj.absolute_url(1)

    def test_zmi_tabs(self):
        for view in self.zmi_tabs:
            response = self.publish('%s/%s' % (self.obj_path, view), self.owner_auth)
            self.assertStatusEqual(response.getStatus(), 200, 
                "%s: %s" % (view, response.getStatus())) # OK

tests.append(TestATCTToolFunctional)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite

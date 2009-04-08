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
"""Test module for bug reports
"""

__author__ = 'Alec Mitchell <apm13@columbia.edu>'
__docformat__ = 'restructuredtext'

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase
from DateTime import DateTime
import Missing


tests = []

class TestFormatCatalogMetadata(atcttestcase.ATCTSiteTestCase):

    def afterSetUp(self):
        atcttestcase.ATCTSiteTestCase.afterSetUp(self)
        self.script = self.portal.formatCatalogMetadata

    def testFormatDate(self):
        date = '2005-11-02 13:52:25'
        format = '%m-%d-%Y %I:%M %p'
        self.portal.portal_properties.site_properties.manage_changeProperties(
                            localLongTimeFormat='%m-%d-%Y %I:%M %p')
        self.assertEqual(self.script(date),
                         DateTime(date).strftime(format))
        self.assertEqual(self.script(DateTime(date)),
                         DateTime(date).strftime(format))

    def testFormatDict(self):
        self.assertEqual(self.script({'a':1,'b':2}), 'a: 1, b: 2')

    def testFormatList(self):
        self.assertEqual(self.script(('a','b',1,2,3,4)), 'a, b, 1, 2, 3, 4')
        self.assertEqual(self.script(['a','b',1,2,3,4]), 'a, b, 1, 2, 3, 4')
        # this also needs to be able to handle unicode that won't encode to ascii
        ustr = 'i\xc3\xadacute'.decode('utf8')
        self.assertEqual(self.script(['a','b',ustr]), 'a, b, i\xc3\xadacute'.decode('utf8'))

    def testFormatString(self):
        self.assertEqual(self.script('fkj dsh ekjhsdf kjer'), 'fkj dsh ekjhsdf kjer')

    def testFormatTruncates(self):
        self.portal.portal_properties.site_properties.manage_changeProperties(
                            search_results_description_length=12, ellipsis='???')
        self.assertEqual(self.script('fkj dsh ekjhsdf kjer'), 'fkj dsh ekjh???')

    def testFormatStrange(self):
        self.assertEqual(self.script(None), '')
        self.assertEqual(self.script(Missing.Value()), '')

    def testUnicodeValue(self):
        """ Make sure non-ascii encodable unicode is acceptable """
        
        ustr = 'i\xc3\xadacute'.decode('utf8')
        self.assertEqual(self.script(ustr), ustr)

tests.append(TestFormatCatalogMetadata)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite

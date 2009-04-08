##############################################################################
#
# Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Tests for the library tool

$Id: test_resourcetypemapper.py 21075 2005-12-12 12:59:59Z duncan $
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


import unittest
from urlparse import urlsplit, urljoin, urlunsplit
from Products.kupu.plone.html2captioned import makeUrlRelative

class test_urls(unittest.TestCase):
    def test1(self):
        data = 'http://host/site/a'
        base = 'http://host/site/'
        expected = 'a', ''
        self.assertEquals(expected, makeUrlRelative(data, base))

    def testRelativeLinks1(self):
        data =  'http://localhost/cms/folder/jim#_ftnref1'
        expected = "jim", "#_ftnref1"
        base = 'http://localhost/cms/folder/fred'

        self.assertEquals(expected, makeUrlRelative(data, base))

    def testRelativeLinks2(self):
        data =  "http://localhost/cms/folder/otherdoc#key"
        expected = "otherdoc", "#key"
        base = 'http://localhost/cms/folder/'

        self.assertEquals(expected, makeUrlRelative(data, base))

    def testRelativeLinks3(self):
        data =  "http://localhost/cms/otherfolder/otherdoc"
        expected = "../otherfolder/otherdoc", ""
        base = 'http://localhost/cms/folder/'

        self.assertEquals(expected, makeUrlRelative(data, base))

    def testRelativeLinks4(self):
        data =  "http://localhost:9080/plone/Members/admin/art1"
        expected = "", ""
        base = 'http://localhost:9080/plone/Members/admin/art1'

        self.assertEquals(expected, makeUrlRelative(data, base))

    def testRelativeLinks5(self):
        data =  'http://localhost:9080/plone/Members/admin/art1/subitem'
        expected = "art1/subitem", ""
        base = 'http://localhost:9080/plone/Members/admin/art1'

        actual = makeUrlRelative(data, base)
        self.assertEquals(actual, expected)

    def testRelativeLinks6(self):
        data =  "http://localhost:9080/plone/Members/admin"
        expected = ".", ""
        base = 'http://localhost:9080/plone/Members/admin/art1'

        actual = makeUrlRelative(data, base)
        self.assertEquals(actual, expected)

    def testRelativeQuery(self):
        data =  "http://localhost:9080/plone/Members/admin/jim?x=5"
        expected = "jim", "?x=5"
        base = 'http://localhost:9080/plone/Members/admin/art1'

        actual = makeUrlRelative(data, base)
        self.assertEquals(actual, expected)

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(test_urls))
        return suite


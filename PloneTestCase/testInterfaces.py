#
# Interface tests
#

# $Id: testInterfaces.py 39167 2007-03-15 15:11:39Z shh42 $

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import setup
from Products.PloneTestCase.interfaces import *

if setup.Z3INTERFACES:
    from zope.interface.verify import verifyClass
    from zope.interface.verify import verifyObject
else:
    from Interface.Verify import verifyClass
    from Interface.Verify import verifyObject


class TestPloneTestCase(PloneTestCase.PloneTestCase):

    _configure_portal = 0

    def _portal(self):
        return None

    def testIPortalTestCase(self):
        self.failUnless(verifyClass(IPortalTestCase, PloneTestCase.PloneTestCase))
        self.failUnless(verifyObject(IPortalTestCase, self))

    def testIPloneTestCase(self):
        self.failUnless(verifyClass(IPloneTestCase, PloneTestCase.PloneTestCase))
        self.failUnless(verifyObject(IPloneTestCase, self))

    def testIPloneSecurity(self):
        self.failUnless(verifyClass(IPloneSecurity, PloneTestCase.PloneTestCase))
        self.failUnless(verifyObject(IPloneSecurity, self))


class TestFunctionalTestCase(PloneTestCase.FunctionalTestCase):

    _configure_portal = 0

    def _portal(self):
        return None

    def testIFunctional(self):
        self.failUnless(verifyClass(IFunctional, PloneTestCase.FunctionalTestCase))
        self.failUnless(verifyObject(IFunctional, self))

    def testIPortalTestCase(self):
        self.failUnless(verifyClass(IPortalTestCase, PloneTestCase.FunctionalTestCase))
        self.failUnless(verifyObject(IPortalTestCase, self))

    def testIPloneTestCase(self):
        self.failUnless(verifyClass(IPloneTestCase, PloneTestCase.FunctionalTestCase))
        self.failUnless(verifyObject(IPloneTestCase, self))

    def testIPloneSecurity(self):
        self.failUnless(verifyClass(IPloneSecurity, PloneTestCase.FunctionalTestCase))
        self.failUnless(verifyObject(IPloneSecurity, self))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneTestCase))
    suite.addTest(makeSuite(TestFunctionalTestCase))
    return suite

if __name__ == '__main__':
    framework()


#
# Interface tests
#

# $Id: testInterfaces.py 39166 2007-03-15 15:11:23Z shh42 $

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFTestCase import CMFTestCase
from Products.CMFTestCase import setup
from Products.CMFTestCase.interfaces import *

if setup.Z3INTERFACES:
    from zope.interface.verify import verifyClass
    from zope.interface.verify import verifyObject
else:
    from Interface.Verify import verifyClass
    from Interface.Verify import verifyObject


class TestCMFTestCase(CMFTestCase.CMFTestCase):

    _configure_portal = 0

    def _portal(self):
        return None

    def testIPortalTestCase(self):
        self.failUnless(verifyClass(IPortalTestCase, CMFTestCase.CMFTestCase))
        self.failUnless(verifyObject(IPortalTestCase, self))

    def testICMFTestCase(self):
        self.failUnless(verifyClass(ICMFTestCase, CMFTestCase.CMFTestCase))
        self.failUnless(verifyObject(ICMFTestCase, self))

    def testICMFSecurity(self):
        self.failUnless(verifyClass(ICMFSecurity, CMFTestCase.CMFTestCase))
        self.failUnless(verifyObject(ICMFSecurity, self))


class TestFunctionalTestCase(CMFTestCase.FunctionalTestCase):

    _configure_portal = 0

    def _portal(self):
        return None

    def testIFunctional(self):
        self.failUnless(verifyClass(IFunctional, CMFTestCase.FunctionalTestCase))
        self.failUnless(verifyObject(IFunctional, self))

    def testIPortalTestCase(self):
        self.failUnless(verifyClass(IPortalTestCase, CMFTestCase.FunctionalTestCase))
        self.failUnless(verifyObject(IPortalTestCase, self))

    def testICMFTestCase(self):
        self.failUnless(verifyClass(ICMFTestCase, CMFTestCase.FunctionalTestCase))
        self.failUnless(verifyObject(ICMFTestCase, self))

    def testICMFSecurity(self):
        self.failUnless(verifyClass(ICMFSecurity, CMFTestCase.FunctionalTestCase))
        self.failUnless(verifyObject(ICMFSecurity, self))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCMFTestCase))
    suite.addTest(makeSuite(TestFunctionalTestCase))
    return suite

if __name__ == '__main__':
    framework()


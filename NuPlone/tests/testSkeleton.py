#
# This file is a skeleton test suite.
# It is here for letting you add new tests to the product without having to
# modify the existing testStyleInstallation.py module.
# You may modify its name to something that describes what it tests
# (keeping its 'test' prefix).
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase

# CHANGE 'NuPlone' to your product name in the following lines
PloneTestCase.installProduct('NuPlone')
PloneTestCase.setupPloneSite(products=['NuPlone'])


class TestSomething(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        pass

    def testSomething(self):
        # Test something
        self.assertEqual(1+1, 2)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSomething))
    return suite

if __name__ == '__main__':
    framework()

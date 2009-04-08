"""
    QuickInstaller tests.
"""

from Products.CMFTestCase import CMFTestCase
CMFTestCase.installProduct('CMFQuickInstallerTool')
CMFTestCase.installProduct('CMFCalendar')

CMFTestCase.setupCMFSite()

import unittest
from zope.testing import doctest

from Products.GenericSetup import EXTENSION, profile_registry
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

profile_registry.registerProfile('CMFQuickInstallerTool',
           'CMFQuickInstallerTool',
           'Test profile for CMFQuickInstallerTool',
           'profiles/test',
           'CMFQuickInstallerTool',
           EXTENSION,
           for_=None)

def test_suite():
    return unittest.TestSuite((
        Suite('actions.txt',
              optionflags=OPTIONFLAGS,
              package='Products.CMFQuickInstallerTool.tests',
              test_class=CMFTestCase.FunctionalTestCase),
        Suite('install.txt',
              optionflags=OPTIONFLAGS,
              package='Products.CMFQuickInstallerTool.tests',
              test_class=CMFTestCase.FunctionalTestCase),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")

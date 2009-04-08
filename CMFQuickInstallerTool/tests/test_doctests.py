"""
    QuickInstaller tests.
"""

import unittest
from zope.testing.doctestunit import DocTestSuite

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('Products.CMFQuickInstallerTool.QuickInstallerTool'),
        DocTestSuite('Products.CMFQuickInstallerTool.InstalledProduct'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")

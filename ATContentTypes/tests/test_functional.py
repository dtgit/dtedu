# -*- coding: UTF-8 -*-
"""
"""

from Testing import ZopeTestCase
from Products.ATContentTypes.tests.atcttestcase import ATCTFunctionalSiteTestCase 

FILES = ['webdav.txt', 'http_access.txt', 'portaltype_criterion.txt']

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    from Testing.ZopeTestCase import FunctionalDocFileSuite as FileSuite
    for file in FILES:
        suite.addTest(FileSuite(file, package="Products.ATContentTypes.tests",
                                test_class=ATCTFunctionalSiteTestCase)
                     )
    return suite

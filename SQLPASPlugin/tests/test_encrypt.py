import unittest
import doctest
from zope.component import testing
from Testing.ZopeTestCase import zopedoctest
from Products.SQLPASPlugin.tests.basetestcase import BaseTestCase

import Products.Five
import Products.SQLPASPlugin
from Products.Five import zcml

optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

def setUp(test):
    testing.setUp()
    zcml.load_config('meta.zcml', Products.Five)
    zcml.load_config('encrypt.zcml', Products.SQLPASPlugin)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        doctest.DocTestSuite('Products.SQLPASPlugin.encrypt',
                             setUp=setUp,
                             tearDown=testing.tearDown,
                             optionflags=optionflags),
    )
    suite.addTest(
        zopedoctest.ZopeDocFileSuite('encrypt.txt',
                                     package='Products.SQLPASPlugin',
                                     test_class=BaseTestCase)
    )

    return suite

"""
    Status messages tests.
"""

import unittest
from unittest import TestSuite
from zope.testing.doctestunit import DocTestSuite

def test_suite():
    return TestSuite((
        DocTestSuite('Products.statusmessages.adapter'),
        DocTestSuite('Products.statusmessages.message'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")

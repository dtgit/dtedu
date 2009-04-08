import unittest
from Testing.ZopeTestCase import ZopeDocFileSuite
from Testing.ZopeTestCase import FunctionalDocFileSuite

def test_suite():
    if __name__ not in ('five.localsitemanager',
                        'five.localsitemanager.tests',
                        '__main__'):
        # a safety net for when five.localsitemanager is manged into sys.path
        # of a zope2 product
        return unittest.TestSuite()

    return unittest.TestSuite([
        ZopeDocFileSuite('localsitemanager.txt',
                         package="five.localsitemanager"),
        FunctionalDocFileSuite('browser.txt',
                               package="five.localsitemanager")
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

#
# Setup tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.ZCatalog.ZCatalog import ZCatalog

ZopeTestCase.installProduct('ExtendedPathIndex')


class TestSetup(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.folder._setObject('catalog', ZCatalog('catalog'))
        self.catalog = self.folder.catalog

    def assertIndexCreated(self, id):
        try:
            self.catalog.Indexes[id]
        except KeyError:
            self.fail('Failed to create index')

    def testAddIndex(self):
        factory = self.catalog.manage_addProduct['ExtendedPathIndex']
        factory.manage_addExtendedPathIndex(id='path')
        self.assertIndexCreated('path')

    def testAddIndexWithExtra(self):
        factory = self.catalog.manage_addProduct['ExtendedPathIndex']
        factory.manage_addExtendedPathIndex(id='path', extra={'indexed_attrs': 'foo'})
        self.assertIndexCreated('path')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite

if __name__ == '__main__':
    framework()

##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""OFSP export / import support unit tests.

$Id: test_exportimport.py 71212 2006-11-20 19:27:48Z yuppie $
"""

import unittest
import Testing

from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import ExportImportZCMLLayer

_FOLDER_BODY = """\
<?xml version="1.0"?>
<object name="foo_folder" meta_type="Folder">
 <property name="title">Foo</property>
</object>
"""


class FolderXMLAdapterTests(BodyAdapterTestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.OFSP.exportimport import FolderXMLAdapter

        return FolderXMLAdapter

    def _populate(self, obj):
        obj._setPropValue('title', 'Foo')

    def _verifyImport(self, obj):
        self.assertEqual(type(obj.title), str)
        self.assertEqual(obj.title, 'Foo')

    def setUp(self):
        from OFS.Folder import Folder

        BodyAdapterTestCase.setUp(self)
        self._obj = Folder('foo_folder')
        self._BODY = _FOLDER_BODY


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FolderXMLAdapterTests),
        ))

if __name__ == '__main__':
    from Products.GenericSetup.testing import run
    run(test_suite())

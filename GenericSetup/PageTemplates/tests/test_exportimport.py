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
"""PageTemplate export / import support unit tests.

$Id: test_exportimport.py 71212 2006-11-20 19:27:48Z yuppie $
"""

import unittest
import Testing

from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import ExportImportZCMLLayer

_PAGETEMPLATE_BODY = """\
<html>
  <div>Foo</div>
</html>
"""


class ZopePageTemplateBodyAdapterTests(BodyAdapterTestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from Products.GenericSetup.PageTemplates.exportimport \
                import ZopePageTemplateBodyAdapter

        return ZopePageTemplateBodyAdapter

    def _populate(self, obj):
        obj.write(_PAGETEMPLATE_BODY)

    def setUp(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

        BodyAdapterTestCase.setUp(self)
        self._obj = ZopePageTemplate('foo_template')
        self._BODY = _PAGETEMPLATE_BODY


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ZopePageTemplateBodyAdapterTests),
        ))

if __name__ == '__main__':
    from Products.GenericSetup.testing import run
    run(test_suite())

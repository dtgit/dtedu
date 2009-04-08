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
""" Unit test mixin classes and layers.

$Id: testing.py 80863 2007-10-13 16:02:33Z shh $
"""

from OFS.SimpleItem import SimpleItem
from Products.Five import zcml
from zope.app.component.hooks import setHooks
from zope.component import adapts
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.interface import implements
from zope.publisher.interfaces.http import IHTTPRequest
from zope.testing import testrunner
from zope.testing.cleanup import cleanUp

from Products.CMFCore.interfaces import IWorkflowDefinition
from Products.GenericSetup.utils import BodyAdapterBase


class ConformsToFolder:

    def test_folder_z2interfaces(self):
        from Interface.Verify import verifyClass
        from webdav.WriteLockInterface import WriteLockInterface
        from Products.CMFCore.interfaces.Dynamic \
                import DynamicType as IDynamicType
        from Products.CMFCore.interfaces.Folderish \
                import Folderish as IFolderish

        verifyClass(IDynamicType, self._getTargetClass())
        verifyClass(IFolderish, self._getTargetClass())
        verifyClass(WriteLockInterface, self._getTargetClass())

    def test_folder_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from webdav.interfaces import IWriteLock
        from Products.CMFCore.interfaces import IDynamicType
        from Products.CMFCore.interfaces import IFolderish
        from Products.CMFCore.interfaces import IMutableMinimalDublinCore

        verifyClass(IDynamicType, self._getTargetClass())
        verifyClass(IFolderish, self._getTargetClass())
        verifyClass(IMutableMinimalDublinCore, self._getTargetClass())
        verifyClass(IWriteLock, self._getTargetClass())


class ConformsToContent:

    def test_content_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.Contentish \
                import Contentish as IContentish
        from Products.CMFCore.interfaces.DublinCore \
                import CatalogableDublinCore as ICatalogableDublinCore
        from Products.CMFCore.interfaces.DublinCore \
                import DublinCore as IDublinCore
        from Products.CMFCore.interfaces.DublinCore \
                import MutableDublinCore as IMutableDublinCore
        from Products.CMFCore.interfaces.Dynamic \
                import DynamicType as IDynamicType

        verifyClass(ICatalogableDublinCore, self._getTargetClass())
        verifyClass(IContentish, self._getTargetClass())
        verifyClass(IDublinCore, self._getTargetClass())
        verifyClass(IDynamicType, self._getTargetClass())
        verifyClass(IMutableDublinCore, self._getTargetClass())

    def test_content_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFCore.interfaces import ICatalogableDublinCore
        from Products.CMFCore.interfaces import IContentish
        from Products.CMFCore.interfaces import IDublinCore
        from Products.CMFCore.interfaces import IDynamicType
        from Products.CMFCore.interfaces import IMutableDublinCore
        from Products.GenericSetup.interfaces import IDAVAware

        verifyClass(ICatalogableDublinCore, self._getTargetClass())
        verifyClass(IContentish, self._getTargetClass())
        verifyClass(IDAVAware, self._getTargetClass())
        verifyClass(IDublinCore, self._getTargetClass())
        verifyClass(IDynamicType, self._getTargetClass())
        verifyClass(IMutableDublinCore, self._getTargetClass())


class BrowserLanguages(object):

    implements(IUserPreferredLanguages)
    adapts(IHTTPRequest)

    def __init__(self, context):
        self.context = context

    def getPreferredLanguages(self):
        return ('test',)


class EventZCMLLayer:

    @classmethod
    def testSetUp(cls):
        import Products

        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('event.zcml', Products.Five)
        zcml.load_config('event.zcml', Products.CMFCore)
        setHooks()

    @classmethod
    def testTearDown(cls):
        cleanUp()


class TraversingZCMLLayer:

    @classmethod
    def testSetUp(cls):
        import Products.Five

        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('traversing.zcml', Products.Five)
        setHooks()

    @classmethod
    def testTearDown(cls):
        cleanUp()


class TraversingEventZCMLLayer:

    @classmethod
    def testSetUp(cls):
        import Products.Five

        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('traversing.zcml', Products.Five)
        zcml.load_config('event.zcml', Products.Five)
        zcml.load_config('event.zcml', Products.CMFCore)
        setHooks()

    @classmethod
    def testTearDown(cls):
        cleanUp()


class FunctionalZCMLLayer:

    @classmethod
    def setUp(cls):
        import Products

        zcml.load_config('testing.zcml', Products.CMFCore)
        setHooks()

    @classmethod
    def tearDown(cls):
        cleanUp()


_DUMMY_ZCML = """\
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:five="http://namespaces.zope.org/five"
    i18n_domain="dummy">
  <permission id="dummy.add" title="Add Dummy Workflow"/>
  <five:registerClass
      class="Products.CMFCore.testing.DummyWorkflow"
      meta_type="Dummy Workflow"
      permission="dummy.add"
      addview="addDummyWorkflow.html"
      global="false"
      />
  <adapter
      factory="Products.CMFCore.testing.DummyWorkflowBodyAdapter"
      provides="Products.GenericSetup.interfaces.IBody"
      for="Products.CMFCore.interfaces.IWorkflowDefinition
           Products.GenericSetup.interfaces.ISetupEnviron"
      />
</configure>
"""


class DummyWorkflow(SimpleItem):

    implements(IWorkflowDefinition)

    meta_type = 'Dummy Workflow'

    def __init__(self, id):
        self._id = id

    def getId(self):
        return self._id


class DummyWorkflowBodyAdapter(BodyAdapterBase):

    body = property(BodyAdapterBase._exportBody, BodyAdapterBase._importBody)


class ExportImportZCMLLayer:

    @classmethod
    def testSetUp(cls):
        import Products.Five
        import Products.GenericSetup
        import Products.CMFCore
        import Products.CMFCore.exportimport

        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.GenericSetup)
        zcml.load_config('tool.zcml', Products.CMFCore)
        zcml.load_config('configure.zcml', Products.CMFCore.exportimport)
        zcml.load_string(_DUMMY_ZCML)
        setHooks()

    @classmethod
    def testTearDown(cls):
        cleanUp()


# Derive from ZopeLite layer if available
try:
    from Testing.ZopeTestCase.layer import ZopeLite
except ImportError:
    pass # Zope < 2.11
else:
    EventZCMLLayer.__bases__ = (ZopeLite,)
    TraversingZCMLLayer.__bases__ = (ZopeLite,)
    TraversingEventZCMLLayer.__bases__ = (ZopeLite,)
    FunctionalZCMLLayer.__bases__ = (ZopeLite,)
    ExportImportZCMLLayer.__bases__ = (ZopeLite,)


def run(test_suite):
    options = testrunner.get_options()
    options.resume_layer = None
    options.resume_number = 0
    testrunner.run_with_options(options, test_suite)

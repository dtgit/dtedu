##############################################################################
#
# Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Tests for the drawer support code

$Id$
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.ptc import portal_owner

PloneTestCase.setupPloneSite(products=['kupu'])

from AccessControl.SecurityManagement import newSecurityManager
try:
    from Products.ATContentTypes.lib import constraintypes
except ImportError:
    constraintypes = None

from Products.kupu.plone.tests import TestContent

RESOURCES = dict(
    linkable = ('Document', 'Image', 'File', 'Folder'),
    mediaobject = ('Image',),
    collection = ('Folder',),
    containsanchors = ('Document',),
    )

# Type names vary according to the version of Plone and/or
# ATContentTypes. Map the new names to the old ones here, and
# turn it into an identity mapping later if we can.
TypeMapping = {
    'Document': 'ATDocument',
    'Image': 'ATImage',
    'Link': 'ATLink',
    'Folder': 'ATFolder',
    'File': 'ATFile',
    'News Item': 'ATNewsItem',
    'Event': 'ATEvent',
}
def MapType(typename):
    return TypeMapping[typename]

class TestPloneDrawer(PloneTestCase.PloneTestCase):
    """Test the implementation of the PloneDrawer class"""

    def afterSetUp(self):
        portal = self.portal
        self.setRoles(['Manager',])
        self.kupu = portal.kupu_library_tool
        typestool = self.portal.portal_types
        if not hasattr(typestool, 'ATDocument'):
            # Use the type names without the AT prefix
            for k in TypeMapping:
                TypeMapping[k] = k

    def loginPortalOwner(self):
        '''Use if you need to manipulate the portal itself.'''
        uf = self.app.acl_users
        user = uf.getUserById(portal_owner).__of__(uf)
        newSecurityManager(None, user)

    def create(self, id, metatype='ATDocument', folder=None, **kwds):
        '''Create an object in the cms portal'''
        if folder is None:
            folder = self.portal

        folder.invokeFactory(MapType(metatype), id)
        obj = getattr(folder, id)

        if metatype=='Folder' and constraintypes:
            obj.setConstrainTypesMode(constraintypes.DISABLED)

        if metatype=='Document':
            obj.setTitle('Simple document')
            obj.setText('Sample document text')
            for k, v in kwds.items():
                field = obj.getField(k)
                mutator = field.getMutator(obj)(v)

            obj.reindexObject()
        return obj

    def setup_content(self):
        self.setRoles(['Manager',])
        self.loginPortalOwner()
        f = self.create('folder', 'Folder')

        for id in ('alpha', 'beta'):
            self.create(id, 'Document', f, subject=['aspidistra'])
        self.create('gamma', 'Document', f)

        sub1 = self.create('sub1', 'Folder', f)
        sub1.setSubject(['aspidistra'])
        sub1.reindexObject()
        sub2 = self.create('sub2', 'Folder', f)
        self.create('delta', 'Folder', sub2)

        portal = self.portal
        tool = self.portal.kupu_library_tool
        types = tool.zmi_get_resourcetypes()
        #tool.deleteResource([ t.name for t in types])
        for k,v in RESOURCES.items():
            tool.addResourceType(k, [MapType(t) for t in v])

    def test_FolderContents1(self):
        def assertKey(item, key, expected):
            actual =  item.get(key, None)
            self.assertEquals(expected, actual,
                "Item %s.%s expected %s got %s" % (UIDS[item['id']], key, expected, actual))

        self.setup_content()
        portal = self.portal
        folder = portal['folder']
        UIDS = {}
        for id in folder.objectIds():
            UIDS[folder[id].UID()] = id

        # Allows browse: docs + folders
        items = self.kupu.getFolderItems(folder, resource_type='TestContent.multiRef')
        ids = [UIDS[t['id']] for t in items]
        self.assertEquals(['alpha', 'beta', 'gamma', 'sub1', 'sub2'], ids)

        # No browse: docs only.
        items = self.kupu.getFolderItems(folder, resource_type='TestContent.multiRef2')
        ids = [UIDS[t['id']] for t in items]
        self.assertEquals(['alpha', 'beta', 'gamma'], ids)

    def test_FolderWithKeywords(self):
        def assertKey(item, key, expected):
            actual =  item.get(key, None)
            self.assertEquals(expected, actual,
                "Item %s.%s expected %s got %s" % (UIDS[item['id']], key, expected, actual))

        self.setup_content()
        portal = self.portal
        folder = portal['folder']
        UIDS = {}
        for id in folder.objectIds():
            UIDS[folder[id].UID()] = id

        # Query restriction: keyword match only, but should include
        # both folders.
        items = self.kupu.getFolderItems(folder, resource_type='TestContent.multiRef3')
        ids = [UIDS[t['id']] for t in items]
        self.assertEquals(['alpha', 'beta', 'sub1', 'sub2'], ids)
        # Now check that only the first of the two folders is linkable...
        for t in items[:-1]:
            assertKey(t, 'linkable', True)
        assertKey(items[-1], 'linkable', None)

        for t in items[:-2]:
            assertKey(t, 'anchor', True)
        assertKey(items[-2], 'anchor', False)
        assertKey(items[-1], 'anchor', False)

        # Both folders should contain a src element.
        self.assert_(items[-1]['src'])
        self.assert_(items[-2]['src'])

    def test_NoBrowseWithKeywords(self):
        def assertKey(item, key, expected):
            actual =  item.get(key, None)
            self.assertEquals(expected, actual,
                "Item %s.%s expected %s got %s" % (UIDS[item['id']], key, expected, actual))

        self.setup_content()
        portal = self.portal
        folder = portal['folder']
        UIDS = {}
        for id in folder.objectIds():
            UIDS[folder[id].UID()] = id

        # Query restriction: keyword match only, and since we don't
        # allow browse only 1 folder (non-browsable)
        items = self.kupu.getFolderItems(folder, resource_type='TestContent.multiRef4')
        ids = [UIDS[t['id']] for t in items]
        self.assertEquals(['alpha', 'beta', 'sub1'], ids)
        # Now check that all are linkable and non browsable.
        for t in items[:-1]:
            assertKey(t, 'linkable', True)
            assertKey(t, 'src', None)

    def test_ResourceType(self):
        # Some tests that the ResourceType class is roughly working.
        kupu = self.kupu
        r = kupu.getResourceType('TestContent.multiRef2')
        self.assertEquals(r.allow_browse, False)

        r = kupu.getResourceType('linkable')
        self.assertEquals(r.allow_browse, True)
        

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestPloneDrawer))
        return suite

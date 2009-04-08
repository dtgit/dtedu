##############################################################################
#
# Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Base test class for kupu tests"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.ptc import portal_owner

PloneTestCase.setupPloneSite(products=['ATContentTypes', 'kupu'])

from AccessControl.SecurityManagement import newSecurityManager
try:
    from Products.ATContentTypes.lib import constraintypes
except:
    constraintypes = None

from os.path import join, abspath, dirname
PREFIX = abspath(dirname(__file__))

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

class KupuTestCase(PloneTestCase.PloneTestCase):
    """Base class for Kupu tests"""

    def afterSetUp(self):
        portal = self.portal
        self.setRoles(['Manager',])
        self.kupu = portal.kupu_library_tool
        self.kupu.configure_kupu(captioning=True, linkbyuid=True)
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

        assert obj is not None
        return obj

    def setup_content(self):
        self.setRoles(['Manager',])
        self.loginPortalOwner()
        f = self.create('folder', 'Folder')

        for id in ('alpha', 'beta'):
            self.create(id, 'Document', f, subject=['aspidistra'])
        self.create('gamma', 'Image', f)
        gamma = f.gamma
        gamma.setImage(open(join(PREFIX,'image.jpg'),'rb').read())
        gamma.setTitle('Kupu Test Image')
        gamma.setDescription('Test image caption')
        # The image needs a fixed uid for the transform tests.
        f.gamma._setUID('104ede98d4c7c8eaeaa3b984f7395979')
        f.reindexObject()

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

__all__ = ['KupuTestCase', 'PloneTestCase', 'portal_owner']

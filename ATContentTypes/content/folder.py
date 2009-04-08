#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""


"""
__author__  = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'
__old_name__ = 'Products.ATContentTypes.types.ATFolder'

from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import ATCTOrderedFolder
from Products.ATContentTypes.content.base import ATCTBTreeFolder
from Products.ATContentTypes.interfaces import IATFolder
from Products.ATContentTypes.interfaces import IATBTreeFolder
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import NextPreviousAwareSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema
from Products.ATContentTypes.lib.autosort import AutoSortSupport
from Products.ATContentTypes.lib.autosort import AutoOrderSupport

from Products.ATContentTypes import ATCTMessageFactory as _

from Products.CMFCore.permissions import View

ATFolderSchema      = ATContentTypeSchema.copy() + ConstrainTypesMixinSchema + NextPreviousAwareSchema
ATBTreeFolderSchema = ATContentTypeSchema.copy() + ConstrainTypesMixinSchema

finalizeATCTSchema(ATFolderSchema, folderish=True, moveDiscussion=False)
finalizeATCTSchema(ATBTreeFolderSchema, folderish=True, moveDiscussion=False)


class ATFolder(AutoOrderSupport, ATCTOrderedFolder):
    """A folder which can contain other items."""

    schema         =  ATFolderSchema

    portal_type    = 'Folder'
    archetype_name = 'Folder'
    _atct_newTypeFor = {'portal_type' : 'CMF Folder', 'meta_type' : 'Plone Folder'}
    assocMimetypes = ()
    assocFileExt   = ()
    cmf_edit_kws   = ()

    __implements__ = (ATCTOrderedFolder.__implements__, IATFolder,
                     AutoOrderSupport.__implements__)

    # Enable marshalling via WebDAV/FTP/ExternalEditor.
    __dav_marshall__ = True

    security       = ClassSecurityInfo()

    security.declareProtected(View, 'getNextPreviousParentValue')
    def getNextPreviousParentValue(self):
        """If the parent node is also an IATFolder and has next/previous
        navigation enabled, then let this folder have it enabled by
        default as well.
        """
        parent = self.getParentNode()
        from Products.ATContentTypes.interface.folder import IATFolder as IATFolder_
        if IATFolder_.providedBy(parent):
            return parent.getNextPreviousEnabled()
        else:
            return False

    def manage_afterAdd(self, item, container):
        ATCTOrderedFolder.manage_afterAdd(self, item, container)
        AutoOrderSupport.manage_afterAdd(self, item, container)

registerATCT(ATFolder, PROJECTNAME)

class ATBTreeFolder(AutoSortSupport, ATCTBTreeFolder):
    """A folder suitable for holding a very large number of items"""
    schema         =  ATBTreeFolderSchema


    portal_type    = 'Large Plone Folder'
    archetype_name = 'Large Folder'
    _atct_newTypeFor = {'portal_type' : 'CMF Large Plone Folder',
                        'meta_type' : 'Large Plone Folder'}
    assocMimetypes = ()
    assocFileExt   = ()
    cmf_edit_kws   = ()

    __implements__ = (ATCTBTreeFolder.__implements__, IATBTreeFolder,
                      AutoSortSupport.__implements__)

    # Enable marshalling via WebDAV/FTP/ExternalEditor.
    __dav_marshall__ = True

    security       = ClassSecurityInfo()

registerATCT(ATBTreeFolder, PROJECTNAME)

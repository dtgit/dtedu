#########################################################################
# Copyright (c) 2005 Gregoire Weber. 
# All Rights Reserved.
# 
# This file is part of CMFEditions.
# 
# CMFEditions is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# CMFEditions is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with CMFEditions; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#########################################################################
"""Manages Factories for diffrenet kinds of references.

$Id: $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Acquisition import aq_parent, aq_inner
from OFS.OrderedFolder import OrderedFolder

from Products.CMFCore.utils import UniqueObject, getToolByName

from Products.CMFEditions.utilities import generateId

from Products.CMFEditions.interfaces.IReferenceFactories \
    import IReferenceFactories

class ReferenceFactoriesTool(UniqueObject, OrderedFolder):
    __doc__ = __doc__ # copy from module

    __implements__ = (
        IReferenceFactories,
        OrderedFolder.__implements__,   # hide underspecified interfaces :-(
    )
    
    id = 'portal_referencefactories'
    alternative_id = 'portal_referencefactoryregistry'

    meta_type = 'Reference Factory Registry'
    
    security = ClassSecurityInfo()
    
    # be aware that the tool implements also the OrderedObjectManager API
    
    # -------------------------------------------------------------------
    # methods implementing IFactories
    # -------------------------------------------------------------------
    
    security.declarePrivate('invokeFactory')
    def invokeFactory(self, repo_clone, source, selector=None):
        """See IReferenceFactories
        """
        # Just assuming ObjectManager behaviour for now
        portal_hidhandler = getToolByName(self, 'portal_historyidhandler')
        portal_archivist = getToolByName(self, 'portal_archivist')
        try:
            portal_type = repo_clone.getPortalTypeName()
        except AttributeError:
            # We attach the clone directly if the object has no portal type,
            # perhaps we should clone it.
            return repo_clone
        id = repo_clone.getId()
        if id in source.objectIds():
            id = generateId(source, prefix=id)
        # XXX: This makes a lot of changes outside the object scope we :(
        id = source.invokeFactory(portal_type, id)
        obj = getattr(source, id)
        try:
            history_id = portal_hidhandler.getUid(repo_clone)
            portal_hidhandler.setUid(obj, history_id)
        except portal_hidhandler.UniqueIdError:
            portal_hidhandler.register(obj)
        
        return obj

    security.declarePrivate('hasBeenMoved')
    def hasBeenMoved(self, obj, source):
        """See IReferenceFactories
        """
        # Check that the path of the object's parent (by path) is the same as the source
        return aq_parent(aq_inner(obj)).getPhysicalPath() != source.getPhysicalPath()

InitializeClass(ReferenceFactoriesTool)

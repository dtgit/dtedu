##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Allow the "view" of a folder to be skinned by type.

$Id: SkinnedFolder.py 68426 2006-06-01 09:25:43Z yuppie $
"""

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from zope.component.factory import Factory
from zope.interface import implements

from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.PortalFolder import PortalFolder

from DublinCore import DefaultDublinCoreImpl
from permissions import ModifyPortalContent
from permissions import View


class SkinnedFolder(CMFCatalogAware, PortalFolder):

    """ Skinned Folder class. 
    """

    implements(IContentish)

    security = ClassSecurityInfo()

    manage_options = PortalFolder.manage_options

    # XXX: maybe we should subclass from DefaultDublinCoreImpl or refactor it

    security.declarePrivate('notifyModified')
    def notifyModified(self):
        """ Take appropriate action after the resource has been modified.

        Update creators.
        """
        self.addCreator()

    security.declareProtected(ModifyPortalContent, 'addCreator')
    addCreator = DefaultDublinCoreImpl.addCreator.im_func

    security.declareProtected(View, 'listCreators')
    listCreators = DefaultDublinCoreImpl.listCreators.im_func

    security.declareProtected(View, 'Creator')
    Creator = DefaultDublinCoreImpl.Creator.im_func

    # We derive from CMFCatalogAware first, so we are cataloged too.

    #
    #   IContentish method
    #

    security.declareProtected(View, 'SearchableText')
    def SearchableText(self):
        """
        SeachableText is used for full text seraches of a portal.  It
        should return a concatenation of all useful text.
        """
        return "%s %s" % (self.title, self.description)

InitializeClass(SkinnedFolder)

SkinnedFolderFactory = Factory(SkinnedFolder)

def addSkinnedFolder( self, id, title='', description='', REQUEST=None ):
    """
    """
    sf = SkinnedFolder( id, title )
    sf.description = description
    self._setObject( id, sf )
    sf = self._getOb( id )
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( sf.absolute_url() + '/manage_main' )

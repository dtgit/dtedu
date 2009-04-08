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
""" Basic portal discussion access tool.

$Id: DiscussionTool.py 81923 2007-11-18 22:51:13Z jens $
"""

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Globals import DTMLFile
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from zope.interface import implements

from Products.CMFCore.interfaces import IDiscussionResponse
from Products.CMFCore.interfaces import IDiscussionTool
from Products.CMFCore.interfaces.Discussions \
        import DiscussionResponse as z2IDiscussionResponse
from Products.CMFCore.interfaces.portal_discussion \
        import portal_discussion as z2IDiscussionTool
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.utils import UniqueObject

from DiscussionItem import DiscussionItemContainer
from exceptions import AccessControl_Unauthorized
from exceptions import DiscussionNotAllowed
from permissions import ManagePortal
from permissions import ModifyPortalContent
from utils import _dtmldir

_marker = []


class DiscussionTool(UniqueObject, SimpleItem):

    """ Links content to discussions.
    """

    implements(IDiscussionTool)
    __implements__ = (z2IDiscussionTool, )

    id = 'portal_discussion'
    meta_type = 'Default Discussion Tool'

    security = ClassSecurityInfo()

    manage_options = ( ({'label': 'Overview',
                         'action': 'manage_overview'},)
                     + SimpleItem.manage_options
                     )

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile( 'explainDiscussionTool', _dtmldir )

    #
    #   'portal_discussion' interface methods
    #

    security.declarePublic( 'overrideDiscussionFor' )
    def overrideDiscussionFor(self, content, allowDiscussion):
        """ Override discussability for the given object or clear the setting.
        """
        if not _checkPermission(ModifyPortalContent, content):
            raise AccessControl_Unauthorized

        if allowDiscussion is None or allowDiscussion == 'None':
            disc_flag = getattr(aq_base(content), 'allow_discussion', _marker)
            if disc_flag is not _marker:
                try:
                    del content.allow_discussion
                except AttributeError:
                    # https://bugs.launchpad.net/zope-cmf/+bug/162532
                    pass
        else:
            content.allow_discussion = bool(allowDiscussion)

    security.declarePublic( 'getDiscussionFor' )
    def getDiscussionFor(self, content):
        """ Get DiscussionItemContainer for content, create it if necessary.
        """
        if not self.isDiscussionAllowedFor( content ):
            raise DiscussionNotAllowed

        if not IDiscussionResponse.providedBy(content) and \
                not z2IDiscussionResponse.isImplementedBy(content) and \
                getattr( aq_base(content), 'talkback', None ) is None:
            # Discussion Items use the DiscussionItemContainer object of the
            # related content item, so only create one for other content items
            self._createDiscussionFor(content)

        return content.talkback # Return wrapped talkback

    security.declarePublic( 'isDiscussionAllowedFor' )
    def isDiscussionAllowedFor( self, content ):
        """ Get boolean indicating whether discussion is allowed for content.
        """
        if hasattr( aq_base(content), 'allow_discussion' ):
            return bool(content.allow_discussion)
        typeInfo = content.getTypeInfo()
        if typeInfo:
            return bool( typeInfo.allowDiscussion() )
        return False

    #
    #   Utility methods
    #
    security.declarePrivate( '_createDiscussionFor' )
    def _createDiscussionFor( self, content ):
        """ Create DiscussionItemContainer for content, if allowed.
        """
        if not self.isDiscussionAllowedFor( content ):
            raise DiscussionNotAllowed

        content.talkback = DiscussionItemContainer()
        return content.talkback

InitializeClass( DiscussionTool )
registerToolInterface('portal_discussion', IDiscussionTool)

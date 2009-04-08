##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFDefault.interfaces package.

$Id: __init__.py 71020 2006-11-01 15:42:13Z yuppie $
"""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from _content import *
from _tools import *


class ICMFDefaultSkin(IDefaultBrowserLayer):

    """CMF default skin.
    """


# BBB: will be removed in CMF 2.2
#      create zope2 interfaces
from Interface.bridge import createZope3Bridge
import Document
import portal_membership

createZope3Bridge(IDocument, Document, 'IDocument')
createZope3Bridge(IMutableDocument, Document, 'IMutableDocument')
createZope3Bridge(IMembershipTool, portal_membership, 'portal_membership')

del createZope3Bridge

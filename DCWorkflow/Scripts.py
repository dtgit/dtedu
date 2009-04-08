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
""" Scripts in a web-configurable workflow.

$Id: Scripts.py 37044 2005-06-14 18:08:03Z sidnei $
"""

from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from ContainerTab import ContainerTab
from permissions import ManagePortal


class Scripts (ContainerTab):
    """A container for workflow scripts"""

    meta_type = 'Workflow Scripts'

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    def manage_main(self, client=None, REQUEST=None, **kw):
        '''
        '''
        kw['management_view'] = 'Scripts'
        m = Folder.manage_main.__of__(self)
        return m(self, client, REQUEST, **kw)

InitializeClass(Scripts)

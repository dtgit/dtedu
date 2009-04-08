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
""" Product: CMFActionIcons

Define tool for mapping CMF actions onto icons.

$Id: __init__.py 72873 2007-02-27 13:13:44Z yuppie $
"""

from Products.CMFCore.utils import ToolInit

import ActionIconsTool

def initialize(context):

    ToolInit( meta_type='CMF Action Icons Tool'
            , tools=( ActionIconsTool.ActionIconsTool, )
            , icon="tool.gif"
            ).initialize( context )

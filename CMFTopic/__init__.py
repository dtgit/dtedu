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
""" Topic: Canned catalog queries

$Id: __init__.py 72873 2007-02-27 13:13:44Z yuppie $
"""

from Products.CMFCore.utils import ContentInit

import Topic
from permissions import AddTopics


# Make sure security is initialized
import DateCriteria
import ListCriterion
import SimpleIntCriterion
import SimpleStringCriterion
import SortCriterion

def initialize(context):

    context.registerHelpTitle( 'CMF Topic Help' )
    context.registerHelp( directory='help' )

    # BBB: register oldstyle constructors
    ContentInit( 'CMF Topic Content'
               , content_types=()
               , permission=AddTopics
               , extra_constructors=(Topic.addTopic,)
               ).initialize( context )

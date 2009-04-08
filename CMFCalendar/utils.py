##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Utility functions.

$Id: utils.py 41353 2006-01-18 11:05:35Z yuppie $
"""

from AccessControl import ModuleSecurityInfo
from zope.i18nmessageid import MessageFactory


security = ModuleSecurityInfo('Products.CMFCalendar.utils')

security.declarePublic('Message')
Message = MessageFactory('cmf_calendar')

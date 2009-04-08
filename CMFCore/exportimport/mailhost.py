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
"""Mailhost setup handlers.

$Id: mailhost.py 73035 2007-03-07 16:41:03Z jens $
"""

from Products.MailHost.interfaces import IMailHost

from zope.component import getSiteManager

from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects


def importMailHost(context):
    """Import mailhost settings from an XML file.
    """
    sm = getSiteManager(context.getSite())
    tool = sm.getUtility(IMailHost)

    importObjects(tool, '', context)

def exportMailHost(context):
    """Export mailhost settings as an XML file.
    """
    sm = getSiteManager(context.getSite())
    tool = sm.queryUtility(IMailHost)
    if tool is None:
        logger = context.getLogger('mailhost')
        logger.info('Nothing to export.')
        return

    exportObjects(tool, '', context)

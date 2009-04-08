##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser views for favorites.

$Id: favorite.py 76996 2007-06-24 00:18:49Z hannosch $
"""

import urlparse

from zope.app.form.browser import BytesWidget
from zope.component import adapts
from zope.formlib import form
from zope.interface import implements
from zope.interface import Interface
from zope.schema import BytesLine
from zope.schema import TextLine

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.form import ContentEditFormBase
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.interfaces import IMutableFavorite
from Products.CMFDefault.utils import Message as _


class IFavoriteSchema(Interface):

    title = TextLine(
        title=_(u'Title'),
        description=_(u'Title'),
        readonly=True)

    remote_url = BytesLine(
        title=_(u'URL'),
        description=_(u'URL relative to the site root.'),
        required=False,
        missing_value=u'')


class FavoriteSchemaAdapter(SchemaAdapterBase):

    adapts(IMutableFavorite)
    implements(IFavoriteSchema)

    _remote_url = ProxyFieldProperty(IFavoriteSchema['remote_url'])

    def _getRemoteURL(self):
        return self._remote_url

    def _setRemoteURL(self, value):
        self._remote_url = value
        self.context.remote_uid = self.context._getUidByUrl()

    title = ProxyFieldProperty(IFavoriteSchema['title'], 'Title')
    remote_url = property(_getRemoteURL, _setRemoteURL)


class FavoriteURIWidget(BytesWidget):

    """Custom widget for remote_url.
    """

    def _toFieldValue(self, input):
        value = super(FavoriteURIWidget, self)._toFieldValue(input)
        if not value:
            return value
        # strip off scheme and machine from URL if present
        tokens = urlparse.urlparse(value, 'http')
        if tokens[1]:
            # There is a nethost, remove it
            tokens = ('', '') + tokens[2:]
            value = urlparse.urlunparse(tokens)
        # if URL begins with site URL, remove site URL
        obj = self.context.context.context
        portal_url = getToolByName(obj, 'portal_url').getPortalPath()
        if value.startswith(portal_url):
            value = value[len(portal_url):]
        # if site is still absolute, make it relative
        if value[:1]=='/':
            value = value[1:]
        return value


class FavoriteEditView(ContentEditFormBase):

    """Edit view for IMutableFavorite.
    """

    form_fields = form.FormFields(IFavoriteSchema)
    form_fields['remote_url'].custom_widget = FavoriteURIWidget

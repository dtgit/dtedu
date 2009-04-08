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
"""Browser views for links.

$Id: link.py 71045 2006-11-03 17:22:43Z yuppie $
"""

import urlparse

from zope.app.form.browser import BytesWidget
from zope.component import adapts
from zope.formlib import form
from zope.interface import implements
from zope.interface import Interface
from zope.schema import BytesLine
from zope.schema import TextLine

from Products.CMFDefault.formlib.form import ContentEditFormBase
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.interfaces import IMutableLink
from Products.CMFDefault.utils import Message as _

from utils import decode
from utils import memoize
from utils import ViewBase


class ILinkSchema(Interface):

    title = TextLine(
        title=_(u'Title'),
        description=_(u'Title'),
        readonly=True)

    remote_url = BytesLine(
        title=_(u'URL'),
        required=False,
        missing_value=u'')


class LinkSchemaAdapter(SchemaAdapterBase):

    adapts(IMutableLink)
    implements(ILinkSchema)

    title = ProxyFieldProperty(ILinkSchema['title'], 'Title')
    remote_url = ProxyFieldProperty(ILinkSchema['remote_url'])


class LinkView(ViewBase):

    """View for ILink.
    """

    # interface

    @memoize
    @decode
    def url(self):
        return self.context.getRemoteUrl()


class LinkURIWidget(BytesWidget):

    """Custom widget for remote_url.
    """

    def _toFieldValue(self, input):
        value = super(LinkURIWidget, self)._toFieldValue(input)
        if not value:
            return value
        tokens = urlparse.urlparse(value, 'http')
        if tokens[0] == 'http':
            if tokens[1]:
                # We have a nethost. All is well.
                return urlparse.urlunparse(tokens)
            elif tokens[2:] == ('', '', '', ''):
                # Empty URL
                return u''
            else:
                # Relative URL, keep it that way, without http:
                tokens = ('', '') + tokens[2:]
                return urlparse.urlunparse(tokens)
        else:
            # Other scheme, keep original
            return urlparse.urlunparse(tokens)


class LinkEditView(ContentEditFormBase):

    """Edit view for IMutableLink.
    """

    form_fields = form.FormFields(ILinkSchema)
    form_fields['remote_url'].custom_widget = LinkURIWidget

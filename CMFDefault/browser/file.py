##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser views for files.

$Id: file.py 72569 2007-02-14 12:38:28Z yuppie $
"""

from zope.component import adapts
from zope.formlib import form
from zope.interface import implements
from zope.interface import Interface
from zope.schema import ASCIILine
from zope.schema import Bytes
from zope.schema import Text
from zope.schema import TextLine

from Products.CMFDefault.formlib.form import ContentEditFormBase
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.interfaces import IMutableFile
from Products.CMFDefault.utils import Message as _


class IFileSchema(Interface):

    """Schema for file views.
    """

    title = TextLine(
        title=_(u'Title'),
        readonly=True)

    description = Text(
        title=_(u'Description'),
        readonly=True)

    format = ASCIILine(
        title=_(u'Content type'),
        readonly=True)

    upload = Bytes(
        title=_(u'Upload'),
        required=False)


class FileSchemaAdapter(SchemaAdapterBase):

    """Adapter for IMutableFile.
    """

    adapts(IMutableFile)
    implements(IFileSchema)

    title = ProxyFieldProperty(IFileSchema['title'], 'Title')
    description = ProxyFieldProperty(IFileSchema['description'],
                                     'Description')
    format = ProxyFieldProperty(IFileSchema['format'], 'Format')
    upload = ProxyFieldProperty(IFileSchema['upload'],
                                'data', 'manage_upload')


class FileEditView(ContentEditFormBase):

    """Edit view for IMutableFile.
    """

    form_fields = form.FormFields(IFileSchema)

    def setUpWidgets(self, ignore_request=False):
        super(FileEditView,
              self).setUpWidgets(ignore_request=ignore_request)
        self.widgets['description'].height = 3
        self.widgets['upload'].displayWidth = 60

    def _handle_success(self, action, data):
        if not data.get('upload'):
            del data['upload']
        return super(FileEditView, self)._handle_success(action, data)

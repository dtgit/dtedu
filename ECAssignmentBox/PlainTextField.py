# -*- coding: utf-8 -*-
# $Id: PlainTextField.py,v 1.2 2006/04/05 12:27:43 amelung Exp $
#
# Copyright (c) 2006 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECAssignmentBox.
#
# ECAssignmentBox is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECAssignmentBox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECAssignmentBox; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from Products.Archetypes.atapi import *
from AccessControl import ClassSecurityInfo
from Products.Archetypes.utils import mapply
from Products.Archetypes.Field import encode, decode, CHUNK
from Products.Archetypes.Registry import registerField
from Acquisition import aq_base
from Products.Archetypes.interfaces.base import IBaseUnit
from OFS.Image import File
from ZPublisher.HTTPRequest import FileUpload
from OFS.Image import Pdata
from Products.Archetypes.utils import shasattr
from types import FileType
from Products.CMFCore.utils import getToolByName

class PlainTextField(TextField):
    """A specialized field for plain text only"""

    _properties = TextField._properties.copy()
    _properties.update({
        'default_content_type' : 'text/plain',
        })

    security  = ClassSecurityInfo()

    def _process_input(self, value, file=None, default=None,
                       mimetype=None, instance=None, **kwargs):
        """
        """
        if file is None:
            file = self._make_file(self.getName(), title='',
                                   file='', instance=instance)
        filename = kwargs.get('filename') or ''
        body = None
        if IBaseUnit.isImplementedBy(value):
            mimetype = value.getContentType() or mimetype
            filename = value.getFilename() or filename
            return value, mimetype, filename
        elif isinstance(value, self.content_class):
            filename = getattr(value, 'filename', value.getId())
            mimetype = getattr(value, 'content_type', mimetype)
            return value, mimetype, filename
        elif isinstance(value, File):
            # In case someone changes the 'content_class'
            filename = getattr(value, 'filename', value.getId())
            mimetype = getattr(value, 'content_type', mimetype)
            value = value.data
        elif isinstance(value, FileUpload) or shasattr(value, 'filename'):
            filename = value.filename
            # XXX Should be fixed eventually
            body = value.read(CHUNK)
            value.seek(0)
        elif isinstance(value, FileType) or shasattr(value, 'name'):
            # In this case, give preference to a filename that has
            # been detected before. Usually happens when coming from PUT().
            if not filename:
                filename = value.name
                # Should we really special case here?
                for v in (filename, repr(value)):
                    # Windows unnamed temporary file has '<fdopen>' in
                    # repr() and full path in 'file.name'
                    if '<fdopen>' in v:
                        filename = ''
            # XXX Should be fixed eventually
            body = value.read(CHUNK)
            value.seek(0)
        elif isinstance(value, basestring):
            # Let it go, mimetypes_registry will be used below if available
            # if mimetype is None:
            #     mimetype, enc = guess_content_type(filename, value, mimetype)
            pass
        elif isinstance(value, Pdata):
            pass
        elif shasattr(value, 'read') and shasattr(value, 'seek'):
            # Can't get filename from those.
            body = value.read(CHUNK)
            value.seek(0)
        elif value is None:
            # Special case for setDefault.
            value = ''
        else:
            klass = getattr(value, '__class__', None)
            raise TextFieldException('Value is not File or String (%s - %s)' %
                                     (type(value), klass))
        if isinstance(value, Pdata):
            # XXX Should be fixed eventually
            value = str(value)
        filename = filename[max(filename.rfind('/'),
                                filename.rfind('\\'),
                                filename.rfind(':'),
                                )+1:]

        if mimetype is None or mimetype == 'text/x-unknown-content-type':
            if body is None:
                body = value[:CHUNK]
            mtr = getToolByName(instance, 'mimetypes_registry', None)
            if mtr is not None:
                kw = {'mimetype':None,
                      'filename':filename}
                d, f, mimetype = mtr(body, **kw)
            else:
                mimetype, enc = guess_content_type(filename, body, mimetype)
        # mimetype, if coming from request can be like:
        # text/plain; charset='utf-8'
        
        #mimetype = str(mimetype).split(';')[0]
        mimetype = 'text/plain'
        
        file.update(value, instance, mimetype=mimetype, filename=filename)
        file.setContentType(instance, mimetype)
        file.setFilename(filename)
        return file, str(file.getContentType()), file.getFilename()


registerField(PlainTextField,
              title='PlainTextField',
              description='A specialized field for plain text only')

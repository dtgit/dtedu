# Copyright (c) 2002-2006, Benjamin Saller <bcsaller@ideasuite.com>, and 
#	                the respective authors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.	
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following disclaimer
#       in the documentation and/or other materials provided with the
#       distribution. 
#     * Neither the name of Archetypes nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import re
from types import ListType, TupleType
from cStringIO import StringIO
from rfc822 import Message

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Globals import InitializeClass
from OFS.Image import File
from Products.Archetypes.Field import TextField, FileField
from Products.Archetypes.interfaces.marshall import IMarshall
from Products.Archetypes.interfaces.layer import ILayer
from Products.Archetypes.interfaces.base import IBaseUnit
from Products.Archetypes.debug import log
from Products.Archetypes.utils import shasattr
from Products.Archetypes.utils import mapply

try:
    from zope.contenttype import guess_content_type
except ImportError: # BBB: Zope < 2.10
    try:
        from zope.app.content_types import guess_content_type
    except ImportError: # BBB: Zope < 2.9
        from OFS.content_types import guess_content_type

from base import Marshaller

class PrimaryFieldMarshaller(Marshaller):

    security = ClassSecurityInfo()
    security.declareObjectPrivate()
    security.setDefaultAccess('deny')

    def demarshall(self, instance, data, file=None, **kwargs):
        p = instance.getPrimaryField()
        # XXX Hardcoding field types is bad. :(
        if isinstance(p, (FileField, TextField)) and file:
            data = file
        mutator = p.getMutator(instance)
        mutator(data, **kwargs)

    def marshall(self, instance, **kwargs):
        p = instance.getPrimaryField()
        if not p:
            raise TypeError, 'Primary Field could not be found.'
        data = p and instance[p.getName()] or ''
        content_type = length = None
        # Gather/Guess content type
        if IBaseUnit.isImplementedBy(data):
            content_type = data.getContentType()
            length = data.get_size()
            data   = data.getRaw()
        elif isinstance(data, File):
            content_type = data.content_type
            length = data.get_size()
            data = data.data
        else:
            log('WARNING: PrimaryFieldMarshaller(%r): '
                'field %r does not return a IBaseUnit '
                'instance.' % (instance, p.getName()))
            if hasattr(p, 'getContentType'):
                content_type = p.getContentType(instance) or 'text/plain'
            else:
                content_type = (data and guess_content_type(data)
                                or 'text/plain')

            # DM 2004-12-01: "FileField"s represent a major field class
            #  that does not use "IBaseUnit" yet.
            #  Ensure, the used "File" objects get the correct length.
            if hasattr(p, 'get_size'):
                length = p.get_size(instance)
            else:
                # DM: this almost surely is stupid!
                length = len(data)

            # ObjectField without IBaseUnit?
            if shasattr(data, 'data'):
                data = data.data
            else:
                data = str(data)
                # DM 2004-12-01: recompute 'length' as we now know it
                # definitely
                length = len(data)

        return (content_type, length, data)

InitializeClass(PrimaryFieldMarshaller)

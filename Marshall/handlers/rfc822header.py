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

sample_data = r"""title: a title
content-type: text/plain
keywords: foo
mixedCase: a MiXeD case keyword

This is the body.
"""

class NonLoweringMessage(Message):
    """A RFC 822 Message class that doesn't lower header names
    
    IMPORTANT: Only a small subset of the available methods aren't lowering the
               header names!
    """

    def isheader(self, line):
        """Determine whether a given line is a legal header.
        """
        i = line.find(':')
        if i > 0:
            return line[:i]
            #return line[:i].lower()
        else:
            return None        

    def getheader(self, name, default=None):
        """Get the header value for a name.
        """
        try:
            return self.dict[name]
            # return self.dict[name.lower()]
        except KeyError:
            return default
    get = getheader  



def formatRFC822Headers( headers ):

    """ Convert the key-value pairs in 'headers' to valid RFC822-style
        headers, including adding leading whitespace to elements which
        contain newlines in order to preserve continuation-line semantics.

        code based on old cmf1.4 impl 
    """
    munged = []
    linesplit = re.compile( r'[\n\r]+?' )

    for key, value in headers:

        vallines = linesplit.split( value )
        munged.append( '%s: %s' % ( key, '\r\n  '.join( vallines ) ) )

    return '\r\n'.join( munged )

def parseRFC822(body):
    """Parse a RFC 822 (email) style string
    
    The code is mostly based on CMFDefault.utils.parseHeadersBody. It doesn't
    capitalize the headers as the CMF function.
    
    >>> headers, body = parseRFC822(sample_data)
    >>> keys = headers.keys(); keys.sort()
    >>> for key in keys:
    ...     key, headers[key]
    
    
    ('content-type', 'text/plain')
    ('keywords', 'foo')
    ('mixedCase', 'a MiXeD case keyword')
    ('title', 'a title')
    
    >>> print body
    This is the body.
    <BLANKLINE>
    """
    buffer = StringIO(body)
    message = NonLoweringMessage(buffer)
    headers = {}

    for key in message.keys():
        headers[key] = '\n'.join(message.getheaders(key))

    return headers, buffer.read() 

class RFC822Marshaller(Marshaller):

    security = ClassSecurityInfo()
    security.declareObjectPrivate()
    security.setDefaultAccess('deny')

    def demarshall(self, instance, data, **kwargs):
        # We don't want to pass file forward.
        if kwargs.has_key('file'):
            if not data:
                # XXX Yuck! Shouldn't read the whole file, never.
                # OTOH, if you care about large files, you should be
                # using the PrimaryFieldMarshaller or something
                # similar.
                data = kwargs['file'].read()
            del kwargs['file']
        headers, body = parseRFC822(data)
        for k, v in headers.items():
            if v.strip() == 'None':
                v = None
            field = instance.getField(k)
            if field is not None:
                mutator = field.getMutator(instance)
                if mutator is not None:
                    mutator(v)
        content_type = headers.get('Content-Type')
        if not kwargs.get('mimetype', None):
            kwargs.update({'mimetype': content_type})
        p = instance.getPrimaryField()
        if p is not None:
            mutator = p.getMutator(instance)
            if mutator is not None:
                mutator(body, **kwargs)

    def marshall(self, instance, **kwargs):
        p = instance.getPrimaryField()
        body = p and instance[p.getName()] or ''
        pname = p and p.getName() or None
        content_type = length = None
        # Gather/Guess content type
        if IBaseUnit.isImplementedBy(body):
            content_type = str(body.getContentType())
            body   = body.getRaw()
        else:
            if p and hasattr(p, 'getContentType'):
                content_type = p.getContentType(instance) or 'text/plain'
            else:
                content_type = body and guess_content_type(body) or 'text/plain'

        headers = []
        fields = [f for f in instance.Schema().fields()
                  if f.getName() != pname]
        for field in fields:
            if field.type in ('file', 'image', 'object'):
                continue
            accessor = field.getEditAccessor(instance)
            if not accessor:
                continue
            kw = {'raw':1, 'field': field.__name__}
            value = mapply(accessor, **kw)
            if type(value) in [ListType, TupleType]:
                value = '\n'.join([str(v) for v in value])
            headers.append((field.getName(), str(value)))

        headers.append(('Content-Type', content_type or 'text/plain'))

        header = formatRFC822Headers(headers)
        data = '%s\n\n%s' % (header, body)
        length = len(data)

        return (content_type, length, data)

InitializeClass(RFC822Marshaller)

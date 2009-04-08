#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""URL upload

NOT WORKING! experimental code!
"""
__author__  = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'

import urllib2
import urlparse

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from ExtensionClass import Base

from Products.CMFCore.permissions import View

from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.ATContentTypes import permission as ATCTPermissions

from Products.ATContentTypes import ATCTMessageFactory as _

class InvalidContentType(Exception):
    """Invalid content type (uploadFromURL)
    """

urlUploadField = StringField('urlUpload',
        required = False,
        mode = 'w', # write only field
        languageIndependent = True,
        validators = ('isURL',),
        write_permission = ATCTPermissions.UploadViaURL,
        widget = StringWidget(
            description=_(u'help_upload_url',
                          default=u'Upload a file from another server by url.'),
            label = _(u'label_upload_url', default=u'Upload from server'),
            visible={'view' : 'hidden',
                     'edit' : 'hidden'}
            ),
        )

class URLUpload(Base):
    
    security = ClassSecurityInfo()
    
    security.declarePrivate('loadFileFromURL')
    def loadFileFromURL(self, url, contenttypes=()):
        """Loads a file from an url using urllib2

        You can use contenttypes to restrict uploaded content types like:
            ('image',) for all image content types
            ('image/jpeg', 'image/png') only jpeg and png

        May raise an urllib2.URLError based exception or InvalidContentType

        returns file_handler, mimetype, filename, size_in_bytes
        """
        fh = urllib2.urlopen(url)

        info = fh.info()
        mimetype = info.get('content-type', 'application/octetstream')
        size = info.get('content-length', None)

        # scheme, netloc, path, parameters, query, fragment
        path = urlparse.urlparse(fh.geturl())[2]
        if path.endswith('/'):
            pos = -2
        else:
            pos = -1
        filename = path.split('/')[pos]

        success = False
        for ct in contenttypes:
            if ct.find('/') == -1:
                if mimetype[:mimetype.find('/')] == ct:
                    success = True
                    break
            else:
                if mimetype == ct:
                    success = True
                    break
        if not contenttypes:
            success = True
        if not success:
            raise InvalidContentType, mimetype

        return fh, mimetype, filename, size

    security.declareProtected(ATCTPermissions.UploadViaURL, 'setUploadURL')
    def setUrlUpload(self, value, **kwargs):
        """Upload a file from URL
        """
        if not value:
            return
        # XXX no error catching
        fh, mimetype, filename, size = self.loadFileFromURL(value,
                                           contenttypes=('image',))
        mutator = self.getPrimaryField().getMutator(self)
        mutator(fh.read(), mimetype=mimetype, filename=filename)

    security.declareProtected(View, 'getUploadURL')
    def getUrlUpload(self, **kwargs):
        """Always return the default value since we don't store the url
        """
        return self.getField('urlUpload').default

InitializeClass(URLUpload)

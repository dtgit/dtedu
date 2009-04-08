# -*- coding: utf-8 -*-
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
"""AT Content Types configuration file

DO NOT CHANGE THIS FILE!

Use ZConfig to configure ATCT
"""
__docformat__ = 'restructuredtext'

import string
import os
from Products.ATContentTypes.configuration import zconf

## options for mx tidy
## read http://www.egenix.com/files/python/mxTidy.html for more informations
MX_TIDY_ENABLED = zconf.mxtidy.enable
MX_TIDY_OPTIONS= zconf.mxtidy.options

###############################################################################
## private options

PROJECTNAME = "ATContentTypes"
TOOLNAME = "portal_atct"
SKINS_DIR = 'skins'

ATCT_DIR = os.path.abspath(os.path.dirname(__file__))
WWW_DIR = os.path.join(ATCT_DIR, 'www')

GLOBALS = globals()

## swallow PIL exceptions when resizing the image?
SWALLOW_IMAGE_RESIZE_EXCEPTIONS = zconf.swallowImageResizeExceptions.enable

## mxTidy available?
try:
    from mx import Tidy
except ImportError:
    HAS_MX_TIDY = False
else:
    HAS_MX_TIDY = True
    try:
        del Tidy
    except AttributeError:
        pass

## tidy only these document types
MX_TIDY_MIMETYPES = (
    'text/html',
     )

## ExternalStorage available?
try:
    from Products.ExternalStorage.ExternalStorage import ExternalStorage
except ImportError:
    HAS_EXT_STORAGE = False
else:
    HAS_EXT_STORAGE = True
    del ExternalStorage

## LinguaPlone addon?
try:
    from Products.LinguaPlone.public import registerType
except ImportError:
    HAS_LINGUA_PLONE = False
else:
    HAS_LINGUA_PLONE = True
    del registerType

try:
    from PIL import Image
except ImportError:
    HAS_PIL = False
else:
    HAS_PIL = True


## workflow mapping for the installer
WORKFLOW_DEFAULT  = '(Default)'
WORKFLOW_FOLDER   = 'folder_workflow'
WORKFLOW_TOPIC    = 'folder_workflow'
WORKFLOW_CRITERIA = ''

## icon map used for overwriting ATFile icons
ICONMAP = {'application/pdf' : 'pdf_icon.gif',
           'image'           : 'image_icon.gif'}

MIME_ALIAS = {
    'plain' : 'text/plain',
    'stx'   : 'text/structured',
    'html'  : 'text/html',
    'rest'  : 'text/x-rst',
    'text/stx' : 'text/structured',
    'structured-text' : 'text/structured',
    'restructuredtext' : 'text/x-rst',
    'text/restructured' : 'text/x-rst',
    }

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
#  You should have received a copy of the GNU Gefneral Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""ATCT ZConfig loader

"""
__author__  = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'

import os

from ZConfig.loader import ConfigLoader
from Globals import INSTANCE_HOME
from Products.ATContentTypes.configuration.schema import atctSchema

# directories
INSTANCE_ETC = os.path.join(INSTANCE_HOME, 'etc')
_here = os.path.dirname(__file__)
ATCT_HOME = os.path.dirname(os.path.abspath(os.path.join(_here)))
ATCT_ETC = os.path.join(ATCT_HOME, 'etc')

# files
CONFIG_NAME = 'atcontenttypes.conf'
INSTANCE_CONFIG = os.path.join(INSTANCE_ETC, CONFIG_NAME)
ATCT_CONFIG = os.path.join(ATCT_ETC, CONFIG_NAME)
ATCT_CONFIG_IN = os.path.join(ATCT_ETC, CONFIG_NAME+'.in')

# check files for existence
if not os.path.isfile(INSTANCE_CONFIG):
    INSTANCE_CONFIG = None
if not os.path.isfile(ATCT_CONFIG):
    ATCT_CONFIG = None
if not os.path.isfile(ATCT_CONFIG_IN):
    raise RuntimeError("Unable to find configuration file at %s" % 
                        ATCT_CONFIG_IN)
FILES = (INSTANCE_CONFIG, ATCT_CONFIG, ATCT_CONFIG_IN,)

# config
zconf, handler, conf_file = None, None, None
def loadConfig(files, schema=atctSchema, overwrite=False):
    """Config loader
    
    The config loader tries to load the first existing file
    """
    global zconf, handler, conf_file
    if not isinstance(files, (tuple, list)):
        files = (files, )
    if zconf is not None and not overwrite:
        raise RuntimeError, 'Configuration is already loaded'
    for file in files:
        if file is not None:
            if not os.path.exists(file):
                raise RuntimeError, '%s does not exist' % file
            conf_file = file
            zconf, handler = ConfigLoader(schema).loadURL(conf_file)
            break


loadConfig(FILES)

__all__ = ('zconf', 'handler', 'conf_file')

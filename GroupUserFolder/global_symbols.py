# -*- coding: utf-8 -*-
## GroupUserFolder
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

"""
__version__ = "$Revision:  $"
# $Source:  $
# $Id: global_symbols.py 32384 2006-10-27 10:00:55Z encolpe $
__docformat__ = 'restructuredtext'

import os
import string

# Check if we have to be in debug mode
import Log
if os.path.isfile(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'debug.txt')):
    Log.LOG_LEVEL = Log.LOG_DEBUG
    DEBUG_MODE = 1
else:
    Log.LOG_LEVEL = Log.LOG_NOTICE
    DEBUG_MODE = 0

from Log import *

# Retreive version
if os.path.isfile(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'version.txt')):
    __version_file_ = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'version.txt'), 'r', )
    version__ = __version_file_.read()[:-1]
    __version_file_.close()
else:
    version__ = "(UNKNOWN)"

# Check if we are in preview mode
PREVIEW_PLONE21_IN_PLONE20_ = 0
splitdir = os.path.split(os.path.abspath(os.path.dirname(__file__)))
products = os.path.join(*splitdir[:-1])
version_file = os.path.join(products, 'CMFPlone', 'version.txt')
if os.path.isfile(version_file):
    # We check if we have Plone 2.0
    f = open(version_file, "r")
    v = f.read()
    f.close()
    if string.find(v, "2.0.") != -1:
        PREVIEW_PLONE21_IN_PLONE20_ = 1


# Group prefix
GROUP_PREFIX = "group_"
GROUP_PREFIX_LEN = len(GROUP_PREFIX)

# Batching range for ZMI pages
MAX_USERS_PER_PAGE = 100

# Max allowrd users or groups to enable tree view
MAX_TREE_USERS_AND_GROUPS = 100

# Users/groups tree cache time (in seconds)
# This is used in management screens only
TREE_CACHE_TIME = 10

# List of user names that are likely not to be valid user names.
# This list is for performance reasons in ZMI views. If some actual user names
# are inside this list, management screens won't work for them but they
# will still be able to authenticate.
INVALID_USER_NAMES = [
    'BASEPATH1', 'BASEPATH2', 'BASEPATH3', 'a_', 'URL', 'acl_users', 'misc_',
    'management_view', 'management_page_charset', 'REQUEST', 'RESPONSE',
    'MANAGE_TABS_NO_BANNER', 'tree-item-url', 'SCRIPT_NAME', 'n_', 'help_topic',
    'Zope-Version', 'target',
    ]

# LDAPUserFolder-specific stuff
LDAPUF_METHOD = "manage_addLDAPSchemaItem"      # sample method to determine if a uf is an ldapuf
LDAP_GROUP_RDN = "cn"                           # rdn attribute for groups

LOCALROLE_BLOCK_PROPERTY = "__ac_local_roles_block__"           # Property used for lr blocking

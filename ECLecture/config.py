# -*- coding: utf-8 -*-
# $Id: config.py,v 1.4 2006/04/12 12:25:10 amelung Exp $
#
# Copyright (c) 2006 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECLecture.
#
# ECLecture is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECLecture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECLecture; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from Products.CMFCore import permissions

GLOBALS = globals()

I18N_DOMAIN = 'eduComponents'

# define skins directory
SKINS_DIR = 'skins'

# define dependencies
DEPENDENCIES = ['DataGridField']

# define product and tool names
PRODUCT_NAME = 'ECLecture'

ECL_NAME  = 'ECLecture'
ECL_TITLE = 'Lecture'
ECL_META  = ECL_NAME
ECL_ICON  = 'eclecture.png'

# define permissions
add_permission  = permissions.AddPortalContent
edit_permission = permissions.ModifyPortalContent
view_permission = permissions.View

# define text types
TEXT_TYPES = (
    'text/structured',
    'text/x-rst',
    'text/html',
    'text/plain',
    )

# some LOG levels
BLATHER=-100
DEBUG=-200
TRACE=-300

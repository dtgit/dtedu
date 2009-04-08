## Script (Python) "ecl_participants_export"
##parameters=format='tab'
##title=
##

# -*- coding: iso-8859-1 -*-
# $Id: ecl_participants_export.py,v 1.1 2007/03/16 12:55:15 mxp Exp $
#
# Copyright © 2007 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECLecture.
#
# ECLecture is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECLecture is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECLecture; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

REQUEST  = context.REQUEST
RESPONSE = REQUEST.RESPONSE

from AccessControl import getSecurityManager

try:
    ecab_utils = context.ecab_utils
except:
    ecab_utils = None

I18N_DOMAIN='eduComponents'

target = context.getActionInfo('object/ecl_participants')['url']
REDIRECT_URL = '%s?portal_status_message=' % target

# Unless some participants were explicitly selected, export all
# participants
filter = False
if REQUEST.has_key('ids'):
    filter = True

# Define the export format
exportFormat   = ['tab', '\t', '\n', '"', '"', '"']
colDelim       = exportFormat[1]
rowDelim       = exportFormat[2]
strStart       = exportFormat[3]
strEnd         = exportFormat[4]
escapeChar     = exportFormat[5]
exportEncoding = 'iso-8859-15'
siteEncoding   = context.getCharset()

###############################################################################

def escape(string):
    escaped = ''
    for c in string:
        if(c in [escapeChar, strStart, strEnd]):
            escaped += escapeChar + c
        else:
            escaped += c
    return escaped.decode(siteEncoding).encode(exportEncoding)

###############################################################################

table  = []
output = colDelim.join(('fullname', 'username', 'email', 'personaltitle',
                       'studentid', 'major')) + rowDelim

# Create a table containing all required data
participants = context.getGroupMembers(context.getAssociatedGroup())

for p in participants:
    if (not filter) or (filter and p.id in REQUEST.ids):
        username = p.id
        
        if ecab_utils:
            fullname = ecab_utils.getFullNameById(username)
        else:
            fullname = p.fullname
        
        email = p.email
        row = [fullname, username, email,]

        if ecab_utils:
            props = context.portal_properties.ecab_properties
            studentid = ecab_utils.getUserPropertyById(username,
                                                  props.student_id_attr) or ""
            major     = ecab_utils.getUserPropertyById(username,
                                                       props.major_attr) or ""
            perstitle = ecab_utils.getUserPropertyById(username,
                                              props.personal_title_attr) or ""
            row.extend((perstitle, studentid, major,))
        
        table.append(row)

# Sort the table by full name
table.sort(lambda a, b: cmp(a[1], b[1]))

# Create the output
for row in table:
    for i in range(0, len(row)):
        col = row[i]
        if(same_type(col, '') or same_type(col, u'')):
            output += strStart + escape(col) + strEnd
        elif(same_type(col, 1.1)):
            if ecab_utils:
                output += escape(ecab_utils.localizeNumber("%.2f", col))
            else:
                output += escape("%.2f") % col
        else:
            output += escape(str(col))
        
        # Append column delimiter or row delimiter
        output += [colDelim, rowDelim][i >= (len(row) - 1)]

# Generate a filename; the object ID should already be filesystem-safe
filename = '%s_%s.%s' % (context.getId(), 'participants', format)

#RESPONSE.setHeader('Content-Disposition', 'inline') # Useful for debugging
RESPONSE.setHeader('Content-Disposition', 'attachment; filename=' + filename)
RESPONSE.setHeader('Content-Type', 'text/plain')
return output

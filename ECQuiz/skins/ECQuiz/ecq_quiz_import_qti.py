## Script (Python) "importTest"
##parameters=file=''
##title=
##

#!/usr/local/bin/python
# -*- coding: iso-8859-1 -*-
#
# $Id: ecq_quiz_import_qti.py,v 1.4 2007/07/04 01:09:26 wfenske Exp $
#
# Copyright © 2004 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECQuiz.
#
# ECQuiz is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECQuiz is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECQuiz; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

""" This script will be called when somebody presses 'Import' in the 
    import_export form
"""

I18N_DOMAIN = context.i18n_domain

# make sure the quiz is fully created before we import.  otherwise we
# might get AttributeErrors after the import
urlParts = context.absolute_url().split('/')
if (len(urlParts) >= 3) and (urlParts[-3] == 'portal_factory'):
    context = context.portal_factory.doCreate(context)
    context.reindexObject()

if (same_type(file, '') or same_type(file, u'')):
    msg = context.translate(\
        msgid   = 'string_not_file',\
        domain  = I18N_DOMAIN,\
        default = 'Got a string, not a file to read.')
else:
    # Call 'ECQuiz.processQTIImport()"
    addedObjects, errors = context.processQTIImport(file)
    if not errors:
        # The uploaded file seems to be OK.
        msg = context.translate(\
            msgid   = 'file_imported',\
            domain  = I18N_DOMAIN,\
            default = 'The file has been imported.')
    else:
        # The uploaded file has errors.
        msg = context.translate(\
            msgid   = 'errors_occurred',\
            domain  = I18N_DOMAIN,\
            default = 'The following error(s) occurred:') + ' ' \
                + context.str(errors)
    if(addedObjects):
        msg += '\n' + context.translate(\
            msgid   = 'objects_added',\
            domain  = I18N_DOMAIN,\
            default = 'The following objects have been added:') + ' '
        for i in range(0, len(addedObjects)):
            object = addedObjects[i]
            try:
                added = object.title_or_id()
            except:
                added = object
            msg += context.str(added)
            if(i < len(addedObjects) - 1):
                msg += ', '
            else:
                msg += '.'
    else:
        msg += '\n' + context.translate(\
            msgid   = 'nothing_added',\
            domain  = I18N_DOMAIN,\
            default = 'Nothing has been added.')
    msg = msg.replace('\n', ' - ')
    msg = msg.strip()
    msg = context.str(msg)
        
target = context.getActionInfo('object/import_export')['url']
context.redirect('%s?portal_status_message=%s' % (target, msg))

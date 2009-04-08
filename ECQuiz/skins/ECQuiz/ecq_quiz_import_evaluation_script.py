## Script (Python) "uploadEvaluationScript"
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=file='', archetype_name=''
##title=
##

#!/usr/local/bin/python
# -*- coding: iso-8859-1 -*-
#
# $Id: ecq_quiz_import_evaluation_script.py,v 1.2 2007/07/04 01:09:26 wfenske Exp $
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

""" Process custom evaluation script upload forms. This script will
    be called when somebody presses 'Upload' in the 
    upload_evaluation_scripts.pt form.
"""

I18N_DOMAIN = context.i18n_domain

if (same_type(file, '') or same_type(file, u'')):
    msg = context.translate(\
        msgid   = 'string_not_file',\
        domain  = I18N_DOMAIN,\
        default = 'Got a string, not a file to read.')
else:
    # Read the file.
    try:
        functionString = file.filename.read()
    except:
        functionString = file.read()
        
    if( (not functionString) or \
        ( (not same_type(functionString, '')) and (not same_type(functionString, u'')) ) ):
        # The file could not be read.
        msg = context.translate(\
            msgid   = 'file_read_error',\
            domain  = I18N_DOMAIN,\
            default = 'The file could not be read.')
    else:
        # Call 'ECQuiz.processEvaluationScriptUpload()"
        uploadErrorMessage = context.processEvaluationScriptUpload(archetype_name, functionString)
        if not uploadErrorMessage:
            # The uploaded evaluation script seems to be OK.
            msg = context.translate(\
                msgid   = 'script_uploaded',\
                domain  = I18N_DOMAIN,\
                default = 'The script has been uploaded.')
        else:
            # The uploaded evaluation script has errors.
            msg = context.translate(\
                msgid   = 'script_invalid',\
                domain  = I18N_DOMAIN,\
                default = 'The script is invalid. The following error occurred:') + ' ' + uploadErrorMessage
        
target = context.getActionInfo('object/import_export')['url']
context.redirect('%s?portal_status_message=%s' % (target, msg))
